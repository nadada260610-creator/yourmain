import json
import requests
import os
from typing import List, Dict

UPSTAGE_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"
# 권장 모델: solar-1-mini-chat
UPSTAGE_MODEL = "solar-1-mini-chat"

import streamlit as st

def get_api_key() -> str:
    # 1. Streamlit secrets 확인
    if "UPSTAGE_API_KEY" in st.secrets:
        return st.secrets["UPSTAGE_API_KEY"]
    # 2. 환경변수 확인
    return os.environ.get("UPSTAGE_API_KEY", "")

def generate_system_prompt(char_data: dict, summary: str = "") -> str:
    """캐릭터 설정 또는 세계관 데이터를 기반으로 시스템 프롬프트를 생성합니다."""
    # 스토리(세계관) 모드인 경우
    if "system_prompt" in char_data:
        prompt = char_data["system_prompt"]
        if summary:
            prompt += f"\n\n[과거 진행 요약]\n이전까지의 이야기 진행 요약입니다. 이를 기억하고 자연스럽게 이야기에 반영하세요:\n{summary}\n"
        return prompt

    # 일반 캐릭터 모드인 경우
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

def call_upstage(messages: List[Dict[str, str]]) -> str:
    """Upstage API를 호출하여 텍스트를 생성합니다."""
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Upstage API Key가 설정되지 않았습니다. 프로그램 실행 시 환경 변수에 UPSTAGE_API_KEY를 설정하거나 .env 파일을 만들어주세요."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": UPSTAGE_MODEL,
        "messages": messages,
        "stream": False
    }
    
    try:
        response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload, timeout=60)
        
        # API Key 오류 등 인증 실패 처리
        if response.status_code == 401:
            return "⚠️ Upstage API Key 인증에 실패했습니다. 올바른 키인지 확인해주세요."
            
        response.raise_for_status()
        data = response.json()
        
        # Upstage/OpenAI 규격 응답 파싱
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        return "응답을 파싱할 수 없습니다."
        
    except requests.exceptions.RequestException as e:
        print(f"Upstage API Error: {e}")
        return f"Upstage AI 서버 접속에 실패했습니다. 네트워크 상태를 확인해주세요. (에러: {e})"

def summarize_conversation(history: List[Dict[str, str]]) -> str:
    """오래된 대화를 요약하여 장기 기억으로 압축합니다."""
    text_to_summarize = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = "다음 대화 내용을 한국어로 요약해줘. 중요한 사건, 사용자의 기분, 핵심 정보를 중심으로 3~5문장으로 요약해줘:\n\n" + text_to_summarize
    
    messages = [
        {"role": "system", "content": "너는 대화 요약 전문가야."},
        {"role": "user", "content": prompt}
    ]
    
    return call_upstage(messages)

def get_llm_response(user_input: str, char_data: dict, history: List[Dict[str, str]], summary: str) -> str:
    """Upstage LLM을 호출하여 응답을 반환합니다."""
    system_instruction = generate_system_prompt(char_data, summary)
    
    # Upstage API는 messages 배열을 받음
    messages = [
        {"role": "system", "content": system_instruction}
    ]
    
    # 이전 히스토리 추가
    for msg in history:
        # role이 user 또는 assistant여야 함
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
        
    # 현재 사용자 입력 추가
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    return call_upstage(messages)
