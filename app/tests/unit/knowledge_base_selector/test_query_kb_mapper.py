import pytest
from app.backend.DocuSearchAgency.KnowledgeBaseSelector.tools.QueryKBMapper import QueryKBMapper

class TestQueryKBMapper:
    def test_build_mapping_prompt(self, mock_kb_manager):
        mapper = QueryKBMapper(
            kb_manager=mock_kb_manager,
            llm=None,
            query="test query"
        )
        
        prompt = mapper._build_mapping_prompt(
            query="test query",
            available_kbs=mock_kb_manager.list_knowledge_bases()
        )
        
        assert isinstance(prompt, str)
        assert "test query" in prompt
        assert "normes" in prompt