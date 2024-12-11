from agency_swarm.agents import Agent
from typing import Dict, Any

class DocuSearchCEO(Agent):
    def __init__(self):
        super().__init__(
            name="DocuSearchCEO",
            description="The DocuSearchCEO agent coordinates the other agents and manages interactions with the user. It communicates with all other agents in the agency to ensure seamless operation and goal achievement.",
            instructions="./instructions_CEO.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        )
        

    
    def response_validator(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et formate les réponses du CEO"""

        required_fields = ['role', 'content']
        if not all(field in message for field in required_fields):
            raise ValueError(f"Message invalide. Champs requis : {required_fields}")
            
        return message
