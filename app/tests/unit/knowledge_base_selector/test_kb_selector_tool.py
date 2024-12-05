import pytest
from app.backend.DocuSearchAgency.KnowledgeBaseSelector.tools.KBSelectorTool import KBSelectorTool
from app.backend.DocuSearchAgency.KnowledgeBaseSelector.tools.utils.types import SearchFilter, KBFilter, DocumentFilter

class TestKBSelectorTool:
    def test_automatic_selection(self, mock_kb_manager, mock_llm):
        tool = KBSelectorTool(
            query="Quelle est la norme 50125 ?",
            min_relevance=0.6,
            kb_manager=mock_kb_manager,
            llm=mock_llm
        )
        result = tool.run()
        
        assert isinstance(result, dict)
        assert "selected_kbs" in result
        assert len(result["selected_kbs"]) > 0
        assert result["selected_kbs"][0]["kb_id"] == "normes"
        
    def test_manual_selection(self):
        document = DocumentFilter(doc_id="NF_EN_50125-1_2014-1.pdf")
        kb_filter = KBFilter(
            kb_id="normes",
            documents=[document]
        )
        # Créer le SearchFilter avec les bons paramètres
        search_filter = SearchFilter(
            kb_ids=["normes"],
            doc_ids={"normes": ["NF_EN_50125-1_2014-1.pdf"]}
        )
        
        tool = KBSelectorTool(
            query="Test query",
            search_filter=search_filter
        )
        
        result = tool.run()
        assert isinstance(result, dict)
        assert "selected_kbs" in result
        assert len(result["selected_kbs"]) == 1