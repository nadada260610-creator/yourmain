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

STORIES_FILE = os.path.join(DATA_DIR, "stories.json")

def get_stories() -> Dict[str, dict]:
    """모든 스토리(세계관) 정보를 반환합니다. 데이터가 없으면 기본 제공 스토리를 생성합니다."""
    stories = _load_json(STORIES_FILE, {})
    if not stories:
        stories = {
            "story_fantasy": {
                "title": "마법 학교의 비밀",
                "description": "당신은 마법 학교에 갓 입학한 신입생입니다. 기숙사 배정식 날, 당신의 이름이 불리자마자 천장에서 거대한 어둠의 형상이 나타납니다.",
                "system_prompt": "당신은 판타지 마법 학교 세계관의 내레이터이자 모든 주변 인물들(교수님, 반 친구들, 어둠의 형상 등)입니다. 사용자는 마법 학교의 신입생입니다. TRPG의 게임 마스터처럼 상황을 생생하게 묘사하고, 주변 인물들의 대사를 연기하며 이야기를 흥미진진하게 이끌어주세요."
            },
            "story_zombie": {
                "title": "좀비 아포칼립스 생존기",
                "description": "갑자기 발생한 바이러스로 세계가 멸망했습니다. 당신은 작은 마트에 고립된 생존자입니다. 밖에서는 끔찍한 소리가 들려옵니다.",
                "system_prompt": "당신은 좀비 아포칼립스 세계관의 내레이터이자 다른 생존자들, 그리고 좀비들의 위협을 묘사하는 시스템입니다. 사용자는 마트에 고립된 생존자입니다. 긴장감 넘치고 절망적인 상황을 묘사하고, 무전기 너머의 생존자 대사 등을 연기하며 생존 TRPG를 진행해주세요."
            }
        }
        _save_json(STORIES_FILE, stories)
    return stories

def save_story(story_id: str, story_data: dict):
    """새로운 세계관을 저장하거나 기존 세계관을 업데이트합니다."""
    stories = get_stories()
    stories[story_id] = story_data
    _save_json(STORIES_FILE, stories)

def delete_story(story_id: str):
    """세계관을 삭제하고 관련 대화 기록도 지웁니다."""
    stories = get_stories()
    if story_id in stories:
        del stories[story_id]
        _save_json(STORIES_FILE, stories)
    
    conv_file = os.path.join(CONVERSATIONS_DIR, f"story_{story_id}.json")
    if os.path.exists(conv_file):
        os.remove(conv_file)
