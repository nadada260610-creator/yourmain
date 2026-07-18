from utils.llm_manager import get_llm_response, summarize_conversation
from utils.db_manager import get_conversation, save_conversation

def process_chat(user_input: str, char_id: str, char_data: dict) -> str:
    """사용자의 입력을 받아 로컬 AI(Ollama)를 통해 응답을 생성하고 대화 내역을 관리합니다."""
    char_name = char_data.get("name", "아바타")
    
    # 1. Load conversation history
    conv_data = get_conversation(char_id)
    history = conv_data.get("history", [])
    summary = conv_data.get("summary", "")
    
    # 2. Generate response using Local LLM (Ollama)
    response = get_llm_response(user_input, char_data, history, summary)
        
    # 3. Update history
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response})
    
    # 4. Summarize if history is too long
    MAX_TURNS = 10  # 10 turns = 20 messages
    if len(history) >= MAX_TURNS * 2:
        new_summary = summarize_conversation(history)
        # Append to existing summary
        conv_data["summary"] = summary + "\n" + new_summary if summary else new_summary
        # Keep only recent 2 turns (4 messages) to maintain immediate context
        conv_data["history"] = history[-4:]
    else:
        conv_data["history"] = history
        
    # 5. Save updated conversation
    save_conversation(char_id, conv_data)
    
    return response
