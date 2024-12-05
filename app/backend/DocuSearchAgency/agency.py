import os
import sys
from pathlib import Path

# Ajouter le chemin racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agency_swarm import Agency

# Import relatif depuis le même package
from .KnowledgeBaseSelector.KnowledgeBaseSelector import KnowledgeBaseSelector
from .DocuSearchCEO import DocuSearchCEO
from .SemanticSearchAgent import SemanticSearchAgent

docu_search_ceo = DocuSearchCEO()
knowledge_bases_selector = KnowledgeBaseSelector()
semantic_search_agent = SemanticSearchAgent()

agency = Agency([
    docu_search_ceo, #"docu search ceo" will be the entry point for communication with the user
    [docu_search_ceo, semantic_search_agent],
    [docu_search_ceo, knowledge_bases_selector], # "docu search ceo" can initiate communication with "knowledge base selector"
    [knowledge_bases_selector, semantic_search_agent], # "knowledge_bases_selector" can initiate communication with "semantic_search_agent"
    ],
    shared_instructions='./agency_manifesto.md', # shared instructions for all agents
    max_prompt_tokens=25000, # default tokens in conversation for all agents
    temperature=0.3, # default temperature for all agents
)
    
if __name__ == '__main__':
    agency.demo_gradio()
