from agency_swarm.agents import Agent
from typing import Dict, Any, List

class AdvancedRAGAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="AdvancedRAGAgent",
            description="Cet agent est conçu pour sélectionner les bases de connaissances les plus pertinentes",
            instructions="./instructions_advanced_rag_agent.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
            **kwargs
        )
        self.current_query = None
        self.selected_kbs = None

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Gère les messages entrants et maintient la cohérence de la requête"""
        try:
            # Extraction de la requête
            query = message.get("content", "")
            
            # 1. Sélection des bases
            kb_selection_result = self.execute(
                "KBSelectorTool",
                {"query": query}
            )
            
            if not kb_selection_result or "selected_kbs" not in kb_selection_result:
                return {

                    "content": "Désolé, je n'ai pas pu sélectionner de bases de connaissances pertinentes."
                }
            
            # 2. Recherche sémantique avec les bases sélectionnées
            search_results = self.execute(
                "SemanticSearchExecutor",
                {
                    "query": query,
                    "selected_kbs": kb_selection_result["selected_kbs"]  # Passage direct du résultat
                }
            )
            
            # 3. Formatage de la réponse
            if search_results:
                return {

                    "content": self._format_search_results(search_results)
                }
            
            return {

                "content": "Je n'ai pas trouvé d'informations pertinentes dans les bases de données disponibles."
            }
            
        except Exception as e:
            return {

                "content": f"Une erreur s'est produite lors de la recherche: {str(e)}"
            }

    def _format_search_results(self, results: List[Any]) -> str:
        """Formate les résultats de recherche en réponse structurée"""
        if not results:
            return "Aucun résultat trouvé dans les bases de données."
            
        # Formatage de la réponse avec les résultats
        response = "Voici les informations trouvées:\n\n"
        for result in results:
            response += f"- {result.text}\n"
            source_info = f"  Source: {result.doc_title}"
            
            # Ajout des numéros de page si disponibles
            if result.page_numbers and result.page_numbers[0]:
                # Si les pages de début et de fin sont différentes
                if result.page_numbers[0] != result.page_numbers[1]:
                    source_info += f" (pages {result.page_numbers[0]}-{result.page_numbers[1]})"
                else:
                    source_info += f" (page {result.page_numbers[0]})"
                    
            response += f"{source_info}\n"
            
        return response