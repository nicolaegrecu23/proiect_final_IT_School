"""Configurare logger pentru aplicatie."""

import logging
import os

FOLDER = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(FOLDER, "garzi_app.log")

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")