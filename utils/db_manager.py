import json
import os
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Ensure directories exist
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def _load_json(filepath: str, default: Any = None) -> Any:
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default if default is not None else {}

def _save_json(filepath: str, data: Any):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_characters() -> Dict[str, dict]:
    """모든 캐릭터 정보를 반환합니다."""
    return _load_json(CHARACTERS_FILE, {})

def save_character(char_id: str, char_data: dict):
    """새로운 캐릭터를 저장하거나 기존 캐릭터를 업데이트합니다."""
    chars = get_characters()
    chars[char_id] = char_data
    _save_json(CHARACTERS_FILE, chars)

def delete_character(char_id: str):
    """캐릭터와 연관된 데이터를 삭제합니다."""
    chars = get_characters()
    if char_id in chars:
        del chars[char_id]
        _save_json(CHARACTERS_FILE, chars)
    
    # Delete conversation history
    conv_file = os.path.join(CONVERSATIONS_DIR, f"{char_id}.json")
    if os.path.exists(conv_file):
        os.remove(conv_file)

def get_conversation(char_id: str) -> dict:
    """캐릭터와의 대화 내역 및 요약된 기억을 반환합니다."""
    conv_file = os.path.join(CONVERSATIONS_DIR, f"{char_id}.json")
    return _load_json(conv_file, {"history": [], "summary": ""})

def save_conversation(char_id: str, data: dict):
    """캐릭터와의 대화 내역을 저장합니다."""
    conv_file = os.path.join(CONVERSATIONS_DIR, f"{char_id}.json")
    _save_json(conv_file, data)
