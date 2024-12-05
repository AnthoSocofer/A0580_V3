from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict, Optional, Union
from dsrag.database.vector.types import MetadataFilter


class KBFilterBuilder(BaseTool):
    """Construit les filtres de métadonnées pour les recherches"""
    
    kb_id: str = Field(
        ..., description="ID de la base de connaissances"
    )
    doc_ids: Optional[List[str]] = Field(
        None, description="Liste des IDs de documents"
    )
    
    def run(self) -> Optional[MetadataFilter]:
        if not self.doc_ids:
            return None
            
        return {
            "field": "doc_id",
            "operator": "in",
            "value": self.doc_ids
        }