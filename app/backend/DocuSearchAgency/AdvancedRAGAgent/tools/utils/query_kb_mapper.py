import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import re
from agency_swarm.tools import BaseTool
from pydantic import Field, field_validator, ConfigDict

# Ajouter le chemin racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import relatif depuis le même package
from .types import KBMappingResult

class QueryKBMapper(BaseTool):
    """
    Outil responsable de mapper les questions utilisateur aux bases de connaissances pertinentes.
    Utilise une analyse sémantique pour déterminer la pertinence des bases.
    Retourne les deux bases les plus pertinentes dans une liste.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow',
        json_schema_extra={
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Requête utilisateur à analyser"
                },
                "min_relevance": {
                    "type": "number",
                    "description": "Score minimum de pertinence",
                    "default": 0.6
                }
            },
            "required": ["query"]
        }
    )
    
    
    kb_manager: Any = Field(
        ..., 
        description="Gestionnaire des bases de connaissances",
        exclude=True  # Exclure de la sérialisation JSON
    )
    llm: Any = Field(
        ..., 
        description="Service LLM pour l'analyse",
        exclude=True  # Exclure de la sérialisation JSON
    )
    query: str = Field(
        ..., 
        description="Requête utilisateur à analyser"
    )
    min_relevance: float = Field(
        default=0.6, 
        description="Score minimum de pertinence"
    )

    
    def _build_mapping_prompt(self, query: str, available_kbs: List[Dict[str, Any]]) -> str:
        """
        Construit un prompt détaillé pour l'analyse de pertinence.
        """
        kb_descriptions = "\n".join([
            f"- Base:\n  - kb_id_base='{kb['id']}' \n  - Titre= {kb['title']} \n  - Description {kb['description']}"
            for kb in available_kbs
        ])
        
        return f"""En tant qu'expert en analyse de documents, tu dois évaluer la pertinence des bases de connaissances pour la question posée.

RÈGLES IMPORTANTES:
1. Retourner EXACTEMENT le format JSON demandé, sans texte additionnel
2. Maximum 2 bases les plus pertinentes
3. Score minimum de 0.6 obligatoire
4. Les bases mentionnées dans la question reçoivent un score de 1.0
5. Assure toi de bien faire correspondre au champ "kb_id" le champ "kb_id_base" des bases identifiées

Question: "{query}"

Bases disponibles:
{kb_descriptions}

REPONDRE UNIQUEMENT AVEC LE JSON SUIVANT:
{{
  "mappings": [
    {{
      "kb_id": "kb_id_base",
      "relevance_score": 0.95,
      "reasoning": "explication courte de la pertinence"
    }}
  ]
}}"""

    def _extract_json_from_response(self, response: str) -> Dict:
        """
        Extrait et nettoie le JSON de la réponse du LLM de manière robuste.
        """
        try:
            # Essayer d'abord un parsing direct
            return json.loads(response)
        except json.JSONDecodeError:
            try:
                # Chercher un objet JSON dans la réponse
                match = re.search(r'\{[\s\S]*\}', response)
                if match:
                    json_str = match.group(0)
                    return json.loads(json_str)
            except (json.JSONDecodeError, AttributeError):
                # En cas d'échec, construire une réponse par défaut
                return {"mappings": []}

    def _evaluate_kb_relevance(self, mapping_response: Dict, query: str, available_kbs: List[Dict[str, Any]]) -> List[KBMappingResult]:
        """
        Traite la réponse du LLM avec une meilleure gestion des erreurs.
        """
        try:
            # Vérifier si des noms de bases sont mentionnés dans la question
            query_lower = query.lower()
            kb_mentions = {
                kb["id"]: query_lower.find(kb["id"].lower()) != -1 
                for kb in available_kbs
            }
            
            # Récupérer et valider les mappings
            results = []
            mappings = mapping_response.get("mappings", [])
            
            for mapping in mappings:
                try:
                    kb_id = str(mapping.get("kb_id", "")).strip()
                    base_score = float(mapping.get("relevance_score", 0))
                    reasoning = str(mapping.get("reasoning", "")).strip()
                    
                    # Vérifier la validité des données
                    if not kb_id or not any(kb["id"] == kb_id for kb in available_kbs):
                        continue
                        
                    # Attribution du score
                    if kb_mentions.get(kb_id, False):
                        final_score = 1.0
                    else:
                        final_score = max(0.6, min(1.0, base_score))
                    
                    # Ne garder que les scores suffisants
                    if final_score >= 0.6:
                        results.append(KBMappingResult(
                            kb_id=kb_id,
                            relevance_score=final_score,
                            reasoning=reasoning or "Base pertinente pour la requête"
                        ))
                        
                except (ValueError, TypeError):
                    continue
            
            # Tri et sélection finale
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Gérer la priorité de la base "normes"
            normes_mapping = next((m for m in results if m.kb_id == "normes"), None)
            final_results = []
            
            if normes_mapping:
                final_results.append(normes_mapping)
                # Ajouter une deuxième base si disponible
                other_mappings = [m for m in results if m.kb_id != "normes"]
                if other_mappings and len(final_results) < 2:
                    final_results.append(other_mappings[0])
            else:
                # Prendre les deux meilleures bases
                final_results = results[:2]
            
            return final_results
            
        except Exception as e:
            print(f"Erreur dans l'évaluation des mappings: {str(e)}")
            return []

    def map_query_to_kbs(
        self, 
        query: str, 
        min_relevance: float = 0.6
    ) -> List[KBMappingResult]:
        """
        Mappe une question aux bases de connaissances pertinentes.
        """
        try:
            print(f"[QueryKBMapper] Démarrage du mapping pour: {query}")
            available_kbs = self.kb_manager.list_knowledge_bases()
            print(f"[QueryKBMapper] Bases disponibles: {available_kbs}")
            
            if not available_kbs:
                print("[QueryKBMapper] Aucune base de connaissances disponible")
                return []
            
            prompt = self._build_mapping_prompt(query, available_kbs)
            print(f"[QueryKBMapper] Prompt généré: {prompt}")

            response = self.llm.make_llm_call([{
                "role": "user", 
                "content": prompt
            }])
            
            # Extraction et validation du JSON
            json_data = self._extract_json_from_response(response)
            print(f"[QueryKBMapper] Réponse LLM: {response}")

            if not json_data or not isinstance(json_data, dict):
                print("Réponse invalide du LLM")
                return []
            
            # Traitement des mappings
            mappings = self._evaluate_kb_relevance(json_data, query, available_kbs)
            print(f"[QueryKBMapper] Mappings finaux: {mappings}")
            # Vérification finale
            if not mappings:
                print("Aucun mapping valide trouvé")
                return []
                
            return mappings
            
        except Exception as e:
            print(f"Erreur lors du mapping: {str(e)}")
            return []

    def run(self) -> List[KBMappingResult]:
        """
        Méthode requise par BaseTool
        Exécute le mapping de la requête aux bases de connaissances
        """
        return self.map_query_to_kbs(self.query, self.min_relevance)