import sys
import os
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы импорты вида 'from src.Bot...' работали
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))