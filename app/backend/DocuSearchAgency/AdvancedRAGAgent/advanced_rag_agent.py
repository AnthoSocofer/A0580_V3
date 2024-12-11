from agency_swarm.agents import Agent
from typing import Dict, Any

class AdvancedRAGAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="AdvancedRAGAgent",
            description="Cet agent est conçu pour sélectionner les bases de connaissances les plus pertinentes afin de récupérer efficacement des informations à partir d'une requête utilisateur",
            instructions="./instructions_advanced_rag_agent.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
            **kwargs
        )
        
    def response_validator(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et formate les réponses du CEO"""
        # if not isinstance(message, dict):
        #     raise ValueError("Le message doit être un dictionnaire")
            
        # required_fields = ['role', 'content']
        # if not all(field in message for field in required_fields):
        #     raise ValueError(f"Message invalide. Champs requis : {required_fields}")
            
        return message