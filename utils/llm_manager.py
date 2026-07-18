import json
import requests
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/generate"
# 기본 모델은 llama3로 설정 (설치된 모델명에 따라 변경 가능)
OLLAMA_MODEL = "llama3"

def generate_system_prompt(char_data: dict, summary: str = "") -> str:
    """캐릭터 설정 데이터를 기반으로 시스템 프롬프트를 생성합니다."""
    prompt = f"""당신은 AI 어시스턴트가 아니라, 사용자만의 특별한 페르소나입니다. 
아래 설정된 페르소나에 완벽하게 빙의하여 사용자와 한국어로 대화하세요. 절대 자신이 AI라는 것을 밝히지 마세요.

[캐릭터 설정]
- 이름: {char_data.get('name', '이름 없음')}
- 성격: {char_data.get('personality', '평범함')}
- 말투 톤: {char_data.get('tone', '친절한 말투')}
- 배경 이야기: {char_data.get('background', '특별한 배경 없음')}
"""
    few_shot = char_data.get('few_shot', '')
    if few_shot:
        prompt += f"\n[대화 예시]\n{few_shot}\n"
        
    if summary:
        prompt += f"\n[과거 대화 기억(요약)]\n이전에 사용자와 나눈 대화 요약입니다. 이를 기억하고 대화에 활용하세요:\n{summary}\n"
        
    return prompt

def call_ollama(prompt: str, system: str = "") -> str:
    """Ollama API를 호출하여 텍스트를 생성합니다."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Ollama API Error: {e}")
        return f"로컬 AI 서버(Ollama) 접속에 실패했습니다. Ollama가 실행 중인지 확인해주세요. (에러: {e})"

def summarize_conversation(history: List[Dict[str, str]]) -> str:
    """오래된 대화를 요약하여 장기 기억으로 압축합니다."""
    text_to_summarize = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = "다음 대화 내용을 한국어로 요약해줘. 중요한 사건, 사용자의 기분, 핵심 정보를 중심으로 3~5문장으로 요약해줘:\n\n" + text_to_summarize
    
    return call_ollama(prompt=prompt, system="너는 대화 요약 전문가야.")

def get_llm_response(user_input: str, char_data: dict, history: List[Dict[str, str]], summary: str) -> str:
    """로컬 LLM을 호출하여 응답을 반환합니다."""
    system_instruction = generate_system_prompt(char_data, summary)
    
    # Ollama Generate API는 히스토리 배열 자체를 받지 않고 프롬프트 텍스트를 받습니다.
    # 대화 맥락을 프롬프트에 포함하여 전달합니다.
    context_prompt = ""
    for msg in history:
        context_prompt += f"{msg['role']}: {msg['content']}\n"
    
    context_prompt += f"user: {user_input}\nassistant: "
    
    return call_ollama(prompt=context_prompt, system=system_instruction)
