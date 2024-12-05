import pytest
from pathlib import Path
import sys

# Ajouter le chemin racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.backend.DocuSearchAgency.agency import agency
from app.backend.DocuSearchAgency.DocuSearchCEO import DocuSearchCEO
from app.backend.DocuSearchAgency.KnowledgeBaseSelector import KnowledgeBaseSelector

class TestAgency:
    def test_agency_initialization(self):
        """Teste l'initialisation correcte de l'agence"""
        # Vérifier que l'agence est correctement initialisée
        assert agency is not None
        
        # Vérifier que les agents sont correctement instanciés
        assert isinstance(agency.agents[0], DocuSearchCEO)  # Premier agent est le CEO
        assert isinstance(agency.agents[1], KnowledgeBaseSelector)  # Deuxième agent est KnowledgeBaseSelector
        
        # Vérifier la configuration de l'agence
        assert agency.max_prompt_tokens == 25000
        assert agency.temperature == 0.3

    def test_agency_manifesto(self):
        """Teste le chargement du manifeste de l'agence"""
        # Corriger le chemin vers le manifesto
        manifesto_path = Path(__file__).parent.parent.parent / "backend" / "DocuSearchAgency" / "agency_manifesto.md"
        assert manifesto_path.exists(), "Le fichier manifesto doit exister"
        
        # Vérifier que le contenu du manifesto est chargé
        with open(manifesto_path, 'r', encoding='utf-8') as f:
            manifesto_content = f.read()
            assert len(manifesto_content) > 0, "Le manifesto ne doit pas être vide"
            assert "DocuSearchAgency" in manifesto_content, "Le manifesto doit contenir le nom de l'agence"