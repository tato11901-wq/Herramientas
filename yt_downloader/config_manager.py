import json
import os
from pathlib import Path

CONFIG_FILE = "config.json"

def get_default_download_path():
    """Devuelve la ruta de descargas por defecto del sistema."""
    return str(Path.home() / "Downloads")

def load_config():
    """Carga la configuración desde el archivo JSON o devuelve los valores por defecto."""
    if not os.path.exists(CONFIG_FILE):
        return {"download_path": get_default_download_path()}
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"download_path": get_default_download_path()}

def save_config(config_data):
    """Guarda la configuración en el archivo JSON."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
