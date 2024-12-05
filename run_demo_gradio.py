import os
import sys
from pathlib import Path

# Ajouter le chemin du projet au PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.backend.DocuSearchAgency.agency import agency

if __name__ == '__main__':
    agency.demo_gradio(height=900)