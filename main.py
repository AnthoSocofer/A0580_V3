import os
import sys
from pathlib import Path
import logging

# Configure logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

# Add the parent directory to PYTHONPATH
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from app.backend.DocuSearchAgency import DocuSearchAgencyManager, AgencyConfig
import asyncio

async def main():
    agency = None
    try:
        config = AgencyConfig(
            storage_directory="data/knowledge_bases/chromadb",
            temperature=0.3,
            # Supprimons les configurations spécifiques aux agents pour l'instant
            semantic_search_config=None,
            kb_selector_config=None,
            response_generator_config=None
        )
        
        manager = DocuSearchAgencyManager(config)
        agency = manager.get_agency()
        
        # Validate everything works
        health_status = manager.health_check()
        #logger.info("Agency Health Status: %s", health_status)
        
        if all(health_status.values()):
            #logger.info("Agency ready for operation")
            try:
                agency.run_demo()
            except Exception as e:
                #logger.error(f"Erreur lors du lancement de l'application (gradio): {str(e)}")
                print(f"Erreur lors du lancement de l'application (gradio): {str(e)}")
    except Exception as e:
        #logger.error(f"Erreur lors de l'initialisation de l'application: {str(e)}")
        print(f"Erreur lors de l'initialisation de l'application: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())