from agency_swarm.tools import BaseTool
from pydantic import Field, field_validator
from typing import List, Dict, Any, Optional
from dsrag.database.vector.types import MetadataFilter
from .utils import DocumentReference, SearchContext, SearchMode, SearchConfig, KnowledgeBaseManager
from collections import defaultdict

class SemanticSearchExecutor(BaseTool):
    """Outil qui execute des recherches documentaire dans des bases de connaissances"""
    
    query: str = Field(
        ..., 
        description="Search query to execute"
    )
    
    selected_kbs: List[Dict[str, Any]] = Field(
        ..., 
        description="Liste des bases sélectionnées avec leurs filtres et scores"
    )

    @field_validator('selected_kbs')
    def validate_selected_kbs(cls, v):
        if not isinstance(v, list):
            raise ValueError("selected_kbs must be a list")
            
        for kb in v:
            if not isinstance(kb, dict):
                raise ValueError("Each selected_kbs must be a dictionary")
                
            required_fields = {"kb_id", "relevance_score"}
            missing_fields = required_fields - set(kb.keys())
            if missing_fields:
                raise ValueError(f"Missing required fields in selected_kb: {missing_fields}")
                
        return v

    def run(self) -> List[SearchContext]:
        try:
            search_contexts = []
            kb_manager = KnowledgeBaseManager()
            
            # Initialize search configuration with defaults if not provided
            config = SearchConfig(
                mode='BALANCED',
                min_relevance= 0.6,
                max_segments_per_doc= 3,
                adaptive_recall=True,
                enable_fallback=True
            )

            for selection in self.selected_kbs:
                try:
                    kb_id = selection["kb_id"]
                    kb = kb_manager.load_knowledge_base(kb_id)
                    
                    if not kb:
                        print(f"Warning: Knowledge base {kb_id} not found")
                        continue

                    # Get KB metadata for context
                    kb_info = next(
                        (kb for kb in kb_manager.list_knowledge_bases() if kb["id"] == kb_id),
                        {"title": kb_id}
                    )

                    # Execute search with error handling
                    try:
                        results = self._execute_adaptive_search(
                            kb=kb,
                            kb_id=kb_id,
                            query=self.query,
                            metadata_filter=selection.get("metadata_filter"),
                            config=config
                        )

                        if results:
                            search_contexts.append(SearchContext(
                                kb_id=kb_id,
                                results=results,
                                mapping_score=selection["relevance_score"],
                                kb_title=kb_info.get("title")
                            ))
                    except Exception as e:
                        print(f"Error searching in KB {kb_id}: {str(e)}")
                        continue

                except Exception as e:
                    print(f"Error processing KB selection {selection}: {str(e)}")
                    continue

            return search_contexts

        except Exception as e:
            print(f"Critical error in SemanticSearchExecutor: {str(e)}")
            return []

    def _get_rse_params(self, mode: SearchMode) -> dict:
        """Get RSE parameters based on search mode"""
        base_params = {
            SearchMode.PRECISE: {
                'max_length': 10,
                'overall_max_length': 20,
                'minimum_value': 0.7,
                'irrelevant_chunk_penalty': 0.25,
                'decay_rate': 40,
            },
            SearchMode.BALANCED: {
                'max_length': 15,
                'overall_max_length': 30,
                'minimum_value': 0.5,
                'irrelevant_chunk_penalty': 0.18,
                'decay_rate': 30,
            },
            SearchMode.THOROUGH: {
                'max_length': 20,
                'overall_max_length': 40,
                'minimum_value': 0.4,
                'irrelevant_chunk_penalty': 0.15,
                'decay_rate': 25,
            },
            SearchMode.EXHAUSTIVE: {
                'max_length': 25,
                'overall_max_length': 50,
                'minimum_value': 0.3,
                'irrelevant_chunk_penalty': 0.12,
                'decay_rate': 20,
            }
        }

        params = base_params[mode]
        params.update({
            'overall_max_length_extension': 5,
            'top_k_for_document_selection': 10,
            'chunk_length_adjustment': True
        })
        
        return params

    def _execute_adaptive_search(
        self,
        kb,
        kb_id: str,
        query: str,
        metadata_filter: Optional[MetadataFilter],
        config: SearchConfig
    ) -> List[DocumentReference]:
        """Execute search with adaptive recall strategy"""
        try:
            # S'assurer que le mode est un SearchMode valide
            if isinstance(config.mode, str):
                search_mode = SearchMode[config.mode.upper()]
            else:
                search_mode = config.mode
                
            # Initial search with base parameters
            rse_params = self._get_rse_params(search_mode)
            
            results = kb.query(
                search_queries=[query],
                metadata_filter=metadata_filter,
                rse_params=rse_params
            )

            has_valid_results = bool(
                results and 
                any(r.get('score', 0) >= config.min_relevance for r in results)
            )

            # Try adaptive recall if needed
            if not has_valid_results and config.adaptive_recall:
                for mode in [SearchMode.PRECISE, SearchMode.BALANCED, SearchMode.THOROUGH, SearchMode.EXHAUSTIVE]:
                    if mode.value <= config.mode.value:
                        continue
                        
                    adjusted_params = self._get_rse_params(mode)
                    results = kb.query(
                        search_queries=[query],
                        metadata_filter=metadata_filter,
                        rse_params=adjusted_params
                    )
                    
                    if results and any(r.get('score', 0) >= config.min_relevance for r in results):
                        has_valid_results = True
                        break

            if not has_valid_results:
                return []

            # Convert results to DocumentReferences
            doc_references = []
            seen_segments = defaultdict(int)

            for result in results:
                if result.get('score', 0) < config.min_relevance:
                    continue

                try:
                    doc_id = result["doc_id"]
                    if config.max_segments_per_doc > 0:
                        if seen_segments[doc_id] >= config.max_segments_per_doc:
                            continue
                        seen_segments[doc_id] += 1

                    doc_title = kb.chunk_db.get_document_title(doc_id, result["chunk_start"]) or ""
                    doc_info = kb.chunk_db.get_document(doc_id)
                    
                    doc_references.append(DocumentReference(
                        kb_id=kb_id,
                        doc_id=doc_id,
                        doc_title=doc_title,
                        text=result["text"],
                        relevance_score=result["score"],
                        page_numbers=(
                            result.get("chunk_page_start"), 
                            result.get("chunk_page_end")
                        ),
                        metadata=doc_info.get('metadata', {}) if doc_info else {}
                    ))
                except Exception as e:
                    print(f"Error processing result for doc {doc_id}: {str(e)}")
                    continue

            return sorted(doc_references, key=lambda x: x.relevance_score, reverse=True)

        except Exception as e:
            print(f"Erreur lors de la recherche dans {kb_id}: {str(e)}")
            return []