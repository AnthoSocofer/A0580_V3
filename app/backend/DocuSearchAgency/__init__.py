
from .KnowledgeBaseSelector.tools.utils.kb_manager import KnowledgeBaseManager
from .agency import agency
from dataclasses import dataclass
from typing import Optional, Dict, Any
@dataclass
class AgencyConfig:
    """Configuration pour l'agence DocuSearch"""
    storage_directory: str
    temperature: float = 0.3
    semantic_search_config: Optional[Dict[str, Any]] = None
    kb_selector_config: Optional[Dict[str, Any]] = None
    response_generator_config: Optional[Dict[str, Any]] = None

class DocuSearchAgencyManager:
    """Gestionnaire de l'agence DocuSearch"""
    def __init__(self, config: AgencyConfig):
        self.config = config
        self._agency = agency
        
    def get_agency(self):
        """Retourne l'instance de l'agence"""
        return self._agency
        
    def health_check(self) -> Dict[str, bool]:
        """Vérifie l'état de santé de l'agence"""
        return {
            "agency": self._agency is not None,
            "ceo": len(self._agency.agents) > 0,
            "kb_selector": len(self._agency.agents) > 1
        }
__all__ = ['DocuSearchAgencyManager', 'AgencyConfig', 'KnowledgeBaseManager']
