import sys
import os

# Добавляем путь к database_service в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../database_service')))

from models import Match  # Теперь берём из database_service
