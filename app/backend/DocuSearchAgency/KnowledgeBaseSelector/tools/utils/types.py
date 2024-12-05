#app/backend/types/filter_types
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

@dataclass
class KBMappingResult:
    kb_id: str
    relevance_score: float
    reasoning: str

@dataclass
class DocumentFilter:
    doc_id: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Union[str, int, float]]] = None

@dataclass 
class KBFilter:
    kb_id: str
    documents: Optional[List[DocumentFilter]] = None

@dataclass
class SearchFilter:
    """Filtre de recherche unifié pour l'application"""
    kb_ids: Optional[List[str]] = None
    doc_ids: Optional[Dict[str, List[str]]] = None  # kb_id -> [doc_id]
    
    def has_filters(self) -> bool:
        """Vérifie si des filtres sont actifs"""
        return bool(self.kb_ids or self.doc_ids)
    
    def get_kb_ids(self) -> List[str]:
        """Retourne la liste des IDs de bases de connaissances filtrées"""
        if self.kb_ids:
            return self.kb_ids
        if self.doc_ids:
            return list(self.doc_ids.keys())
        return []
    
    def get_doc_ids(self, kb_id: str) -> Optional[List[str]]:
        """Retourne la liste des IDs de documents filtrés pour une base donnée"""
        return self.doc_ids.get(kb_id) if self.doc_ids else None
    
    def to_metadata_filter(self, kb_id: str) -> Optional[Dict[str, Union[str, List[str]]]]:
        """Convertit en filtre de métadonnées pour dsRAG"""
        if self.doc_ids and kb_id in self.doc_ids:
            return {
                "field": "doc_id",
                "operator": "in",
                "value": self.doc_ids[kb_id]
            }
        return None