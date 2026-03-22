import logging
import os
from .config import load_config

config = load_config()

logging.basicConfig(
    level=getattr(logging, config['logging']['level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config['logging']['file']
)

logger = logging.getLogger(__name__)