import pytest
import sys
from pathlib import Path

# Ajouter le chemin racine au PYTHONPATH de manière plus robuste
root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))


@pytest.fixture
def mock_kb_manager():
    class MockKBManager:
        def list_knowledge_bases(self):
            return [
                {
                    "id": "normes",
                    "title": "Normes Ferroviaires",
                    "description": "Base de normes ferroviaires"
                },
                {
                    "id": "procedures",
                    "title": "Procédures",
                    "description": "Procédures techniques"
                }
            ]
    return MockKBManager()

@pytest.fixture
def mock_llm():
    class MockLLM:
        def make_llm_call(self, messages):
            return '''{"mappings": [{"kb_id": "normes", "relevance_score": 0.9, "reasoning": "Test"}]}'''
    return MockLLM()