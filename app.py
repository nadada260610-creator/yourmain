import streamlit as st
import os
import base64
import uuid
from utils.db_manager import get_characters, save_character, delete_character, get_conversation
from utils.chat_engine import process_chat

# Set page config
st.set_page_config(
    page_title="Avatar Garden",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# State initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"
if "selected_char_id" not in st.session_state:
    st.session_state.selected_char_id = "new"

# Hide sidebar only on landing page
if st.session_state.current_page == "landing":
    st.markdown("""
        <style>
        #MainMenu { visibility: hidden !important; }
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { visibility: hidden !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        .stApp { background-color: #000000 !important; }
        
        .block-container {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
            max-width: 100% !important;
            padding: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        #MainMenu { visibility: hidden !important; }
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { visibility: hidden !important; }
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        
        /* 메인 화면(screen01) 바탕색을 흰색으로 강제 지정 */
        .stApp { background-color: #FFFFFF !important; }
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp div, .stApp label { color: #000000 !important; }
        
        /* 사이드바 배경색 흰색으로 변경 */
        [data-testid="stSidebar"] { background-color: #F8F9FA !important; }
        [data-testid="stSidebar"] * { color: #000000 !important; }
        
        /* 텍스트 입력창 배경색 흰색으로 변경 */
        div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CCCCCC !important;
        }
        .stTextInput input, .stTextArea textarea {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- LANDING PAGE ---
if st.session_state.current_page == "landing":
    IMAGE_PATH = os.path.join(BASE_DIR, "assets", "landing.png")
    encoded_string = ""
    if os.path.exists(IMAGE_PATH):
        with open(IMAGE_PATH, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()

        st.markdown(f"""
            <style>
            div.stButton {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                height: 100%;
            }}
            div[data-testid="stButton"] button {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent !important;
                border: none !important;
                width: 80vw !important;
                height: 80vh !important;
                max-width: 1000px;
                box-shadow: none !important;
                transition: transform 0.3s ease;
                color: transparent !important;
            }}
            div[data-testid="stButton"] button:hover {{
                transform: scale(1.05);
                background-color: transparent !important;
                color: transparent !important;
                border: none !important;
            }}
            div[data-testid="stButton"] button:focus, div[data-testid="stButton"] button:active {{
                background-color: transparent !important;
                color: transparent !important;
                box-shadow: none !important;
                border: none !important;
            }}
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("Enter App", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()
    else:
        st.error("assets/landing.png 파일을 찾을 수 없습니다.")

# --- MAIN APP ---
elif st.session_state.current_page == "main":
    # Small neon logo at top left
    st.markdown("<div class='neon-small'>your main</div>", unsafe_allow_html=True)

    chars = get_characters()
    char_options = {"new": "+ 새로운 페르소나 만들기"}
    for cid, cdata in chars.items():
        char_options[cid] = cdata["name"]

    # Sidebar
    if st.sidebar.button("<< 홈으로 돌아가기", use_container_width=True):
        st.session_state.current_page = "landing"
        st.rerun()
        
    st.sidebar.title("나만의 캐릭터")
    st.sidebar.markdown("---")
    
    selected_option = st.sidebar.radio(
        "캐릭터 선택", 
        options=list(char_options.keys()), 
        format_func=lambda x: char_options[x],
        index=list(char_options.keys()).index(st.session_state.selected_char_id) if st.session_state.selected_char_id in char_options else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_char_id = selected_option

    # Delete button
    if selected_option != "new":
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ 이 캐릭터 삭제하기", type="primary", use_container_width=True):
            delete_character(selected_option)
            st.session_state.selected_char_id = "new"
            st.rerun()

    # Main Area
    if st.session_state.selected_char_id == "new":
        st.subheader("새로운 페르소나 생성")
        st.write("어떤 캐릭터와 대화하고 싶으신가요? 프롬프트를 입력하면 즉시 대화방이 열립니다.")
        
        with st.form("quick_create_form"):
            new_name = st.text_input("이름", placeholder="예: 다정씨")
            prompt_text = st.text_area("성격 및 배경 (프롬프트)", placeholder="예: 무뚝뚝하지만 속정이 깊은 카페 사장님. 츤데레 스타일로 말함.", height=150)
            submitted = st.form_submit_button("생성 및 대화 시작하기")
            
            if submitted:
                if new_name and prompt_text:
                    new_id = str(uuid.uuid4())
                    char_data = {
                        "name": new_name,
                        "personality": prompt_text,
                        "tone": "",
                        "background": "",
                        "few_shot": "",
                        "image_path": ""
                    }
                    save_character(new_id, char_data)
                    st.session_state.selected_char_id = new_id
                    st.rerun()
                else:
                    st.error("이름과 프롬프트를 모두 입력해주세요.")
    else:
        # Chat Room
        char_id = st.session_state.selected_char_id
        char_data = chars[char_id]
        
        st.subheader(f"💬 {char_data['name']} 님과의 대화")
        
        # 카카오톡 스타일 메시지 렌더링 함수
        def render_kakaotalk_msg(role, content, char_name=""):
            # HTML 특수문자 처리가 필요할 수 있으나 기본적으로 content 내 태그 허용
            content_html = content.replace('\\n', '<br>')
            if role == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
                    <div style="background-color: #FEE500; color: #000; padding: 10px 15px; border-radius: 15px 0 15px 15px; max-width: 70%; word-break: break-word; font-size: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                        {content_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 15px; align-items: flex-start;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #E2E2E2; margin-right: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;">
                        👤
                    </div>
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-size: 13px; color: #666; margin-bottom: 4px; margin-left: 2px;">{char_name}</span>
                        <div style="background-color: #FFFFFF; color: #000; padding: 10px 15px; border-radius: 0 15px 15px 15px; max-width: 100%; word-break: break-word; border: 1px solid #E5E5E5; font-size: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                            {content_html}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Load history
        conv_data = get_conversation(char_id)
        history = conv_data.get("history", [])
        
        # Display history
        for msg in history:
            render_kakaotalk_msg(msg["role"], msg["content"], char_data['name'])
                
        if prompt := st.chat_input("메시지를 입력하세요..."):
            render_kakaotalk_msg("user", prompt)
            
            with st.spinner(f"{char_data['name']}이(가) 답변을 고민 중입니다..."):
                response = process_chat(prompt, char_id, char_data)
            
            render_kakaotalk_msg("assistant", response, char_data['name'])
