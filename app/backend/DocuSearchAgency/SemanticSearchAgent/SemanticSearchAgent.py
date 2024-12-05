from agency_swarm.agents import Agent
from .tools.SemanticSearchExecutor import SemanticSearchExecutor
from typing import Dict, Any

class SemanticSearchAgent(Agent):
    def __init__(self):
        super().__init__(
            name="SemanticSearchAgent",
            description="The SemanticSearchAgent performs semantic searches in the knowledge bases selected by the KnowledgeBaseSelector. It utilizes a semantic search API to execute these searches effectively.",
            instructions="./instructions_semantic_search.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[SemanticSearchExecutor],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        )
        
    def response_validator(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et formate les réponses du CEO"""
        if not isinstance(message, dict):
            raise ValueError("Le message doit être un dictionnaire")
            
        required_fields = ['role', 'content']
        if not all(field in message for field in required_fields):
            raise ValueError(f"Message invalide. Champs requis : {required_fields}")
            
        return message