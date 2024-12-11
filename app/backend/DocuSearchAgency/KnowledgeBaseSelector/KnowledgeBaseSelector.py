from agency_swarm.agents import Agent
from .tools.KBSelectorTool import KBSelectorTool
from typing import Dict, Any, Optional

class KnowledgeBaseSelector(Agent):
    def __init__(self):
        super().__init__(
            name="KnowledgeBaseSelector",
            description="The KnowledgeBaseSelector agent is responsible for selecting relevant knowledge bases for semantic searches.\
                 It can automatically select knowledge bases or allow the user to choose them manually.",
            instructions="./instructions_kb_selector.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[
                KBSelectorTool,
            ],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        )
    def process_request(self, query: str) -> Dict[str, Any]:
        """
        Processes the request by running the KBSelectorTool and directly passing its output.
        """
        # Initialize the KBSelectorTool with the query
        tool = KBSelectorTool(query=query)
        tool_output = tool.run()

        # Return the output directly without any modification
        return tool_output

    def response_validator(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Directly return the output of KBSelectorTool without modification.
        """
        if not isinstance(message, dict):
             raise ValueError("Le message doit être un dictionnaire")
        return message  # Directly pass the tool's output as is    

    # def response_validator(self, message: Dict[str, Any]) -> Dict[str, Any]:
    #     """Valide et enrichit les réponses de l'agent"""
    #     if not isinstance(message, dict):
    #         raise ValueError("Le message doit être un dictionnaire")

    #     required_fields = ['selected_kbs', 'metadata']
    #     if not all(field in message for field in required_fields):
    #         raise ValueError(f"Message invalide. Champs requis : {required_fields}")

    #     # Enrichissement des métadonnées
    #     message['metadata'].update({
    #         'agent': self.name,
    #         'timestamp': self._get_timestamp(),
    #         'config': self.config
    #     })

    #     if 'selected_kbs' not in message:
    #         raise ValueError("Le message doit contenir la clé 'selected_kbs'")
    
    #     # Ne transmettre que l'output de l'outil
    #     return {'selected_kbs': message['selected_kbs']}


    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()