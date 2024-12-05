import os
import sys
from pathlib import Path

# Ajouter le chemin racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports relatifs depuis le même package
from .utils import SearchFilter, KnowledgeBaseManager, QueryKBMapper, KBFilterBuilder

from dsrag.llm import OpenAIChatAPI
from typing import Dict, List, Any, Optional
from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict, field_validator

class KBSelectorTool(BaseTool):
    """
    Tool for selecting relevant knowledge bases based on query and filters
    Uses QueryKBMapper for automatic selection
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )

    query: str = Field(
        ..., 
        description="User query to analyze"
    )
    search_filter: Optional[SearchFilter] = Field(
        None, 
        description="Optional manual search filters"
    )
    min_relevance: float = Field(
        default=0.6, 
        description="Score minimum de pertinence"
    )
    

    @field_validator('search_filter')
    def validate_search_filter(cls, v):
        if v is not None and not isinstance(v, SearchFilter):
            try:
                return SearchFilter(**v)
            except Exception as e:
                raise ValueError(f"Invalid SearchFilter format: {str(e)}")
        return v

    def run(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute KB selection using either manual filters or QueryKBMapper
        """
        try:
            print(f"[KBSelectorTool] Démarrage avec query: {self.query}")
            print(f"[KBSelectorTool] Filtres manuels: {self.search_filter}")
            
            if self.search_filter and self.search_filter.has_filters():
                result = self._handle_manual_selection()
            else:
                result = self._handle_automatic_selection()
            
            print(f"[KBSelectorTool] Résultat final: {result}")
            return result
            
        except Exception as e:
            print(f"[KBSelectorTool] Erreur critique: {str(e)}")
            return {"selected_kbs": []}
    
    def _handle_manual_selection(self) -> Dict[str, List[Dict[str, Any]]]:
        """Process manual KB selection from filters"""
        selected_kbs = []
        
        for kb_id in self.search_filter.get_kb_ids():
            # Build metadata filter using KBFilterBuilder
            doc_ids = self.search_filter.get_doc_ids(kb_id)
            filter_builder = KBFilterBuilder(kb_id=kb_id, doc_ids=doc_ids)
            metadata_filter = filter_builder.run()
            
            selected_kbs.append({
                "kb_id": kb_id,
                "metadata_filter": metadata_filter,
                "relevance_score": 1.0  # Score maximum pour sélection manuelle
            })
            
        return {"selected_kbs": selected_kbs}
    
    def _handle_automatic_selection(self) -> Dict[str, List[Dict[str, Any]]]:
        """Process automatic KB selection using QueryKBMapper"""
        print("[KBSelectorTool] Démarrage de la sélection automatique")
        kb_manager = KnowledgeBaseManager()  # Instancier le manager
        print(f"[KBSelectorTool] Bases disponibles: {kb_manager.list_knowledge_bases()}")
        
        llm_service = OpenAIChatAPI(  # Utiliser OpenAIChatAPI au lieu de LLM
            model="gpt-4",  # ou un autre modèle disponible
            temperature=0.3,
            max_tokens=1000
        )  # Instancier le service LLM
        
        kb_mapper = QueryKBMapper(
            kb_manager=kb_manager,
            llm=llm_service,
            query=self.query,
            min_relevance=self.min_relevance
        )
        print("[KBSelectorTool] Lancement du mapping")
        mappings = kb_mapper.run()  # Utiliser run() au lieu de map_query_to_kbs
        print(f"[KBSelectorTool] Résultats du mapping: {mappings}")

        selected_kbs = [{
            "kb_id": m.kb_id,
            "metadata_filter": None,
            "relevance_score": m.relevance_score
        } for m in mappings]
        
        return {"selected_kbs": selected_kbs}

if __name__ == "__main__":
    tool = KBSelectorTool(query="Quel est le critère de température T3 de la norme 50125 ?")
    print(tool.run())