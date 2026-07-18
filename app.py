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
        
        /* 추가적인 글로벌 스타일이 필요하면 여기에 작성 */
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
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');
        
        /* 캐릭터 설정 폼 스타일 */
        div[data-testid="stForm"] {
            border: 2px solid #ff0055 !important;
            border-radius: 15px !important;
            padding: 25px !important;
            background-color: rgba(255, 0, 85, 0.03) !important;
            box-shadow: 0 0 10px rgba(255, 0, 85, 0.2) !important;
        }
        
        /* 폼 내부 글씨체 부드럽게 변경 */
        div[data-testid="stForm"] * {
            font-family: 'Gowun Dodum', sans-serif !important;
        }

        .your-main-text {
            font-size: 1.8rem;
            font-weight: 900;
            font-family: 'Courier New', Courier, monospace;
            color: transparent !important;
            -webkit-text-stroke: 1.5px #ff0055;
            text-shadow: 0 0 10px rgba(255,0,85,0.3);
            margin-bottom: 20px;
        }
        .neon-white-text {
            font-weight: 700;
            color: #FFFFFF !important;
            text-shadow: 0 0 5px #fff, 0 0 10px #ff0055, 0 0 20px #ff0055;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Small neon logo at top left
    st.markdown("<div class='your-main-text'>your main</div>", unsafe_allow_html=True)
    chars = get_characters()
    char_options = {"new": "+ 새로운 페르소나 만들기"}
    for cid, cdata in chars.items():
        char_options[cid] = cdata["name"]

    # Sidebar
    if st.sidebar.button("«", type="tertiary", help="첫 화면으로 돌아가기"):
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
        st.markdown("<h3 class='neon-white-text'>나만의 캐릭터 생성</h3>", unsafe_allow_html=True)
        
        if "selected_avatar" not in st.session_state:
            st.session_state.selected_avatar = "1.png"
            
        img_dir = os.path.join(BASE_DIR, "assets", "캐릭터.gnp")
        if os.path.exists(img_dir):
            image_files = sorted([f for f in os.listdir(img_dir) if f.endswith('.png')], key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 999)
            
            st.write("▼ 대화할 캐릭터의 프로필 이미지를 선택하세요")
            
            # 7개의 컬럼으로 그리드 생성 (크기를 더 작게)
            cols = st.columns(7)
            for i, img_file in enumerate(image_files):
                with cols[i % 7]:
                    img_path = os.path.join(img_dir, img_file)
                    
                    # 이미지를 정사각형으로 크기 통일하기 위해 HTML/CSS 강제 적용
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            encoded_img = base64.b64encode(f.read()).decode()
                        st.markdown(f'<img src="data:image/png;base64,{encoded_img}" style="width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 8px; margin-bottom: 5px;">', unsafe_allow_html=True)
                    
                    is_selected = (st.session_state.selected_avatar == img_file)
                    # 볼드체로 선택 버튼 렌더링
                    btn_label = "✅ 선택됨" if is_selected else "선택"
                    
                    # HTML을 사용해 볼드체 적용 (st.button 내부는 마크다운 미지원)
                    if st.button(btn_label, key=f"sel_{img_file}", type="tertiary", use_container_width=True):
                        st.session_state.selected_avatar = img_file
                        st.rerun()
                        
            st.markdown("""
            <style>
            /* type=tertiary 인 버튼을 정확히 타겟팅하기 위한 셀렉터 (Streamlit 버전 호환성 고려) */
            div[data-testid='stButton'] button[data-testid='baseButton-tertiary'],
            div[data-testid='stButton'] button[kind='tertiary'] {
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }
            div[data-testid='stButton'] button[data-testid='baseButton-tertiary'] p,
            div[data-testid='stButton'] button[kind='tertiary'] p { 
                font-weight: 900 !important; 
                color: #ffffff !important;
                text-shadow: 0 0 5px #ff0055, 0 0 10px #ff0055, 0 0 15px #ff0055 !important;
                font-size: 14px;
            }
            div[data-testid='stButton'] button[data-testid='baseButton-tertiary']:hover p,
            div[data-testid='stButton'] button[kind='tertiary']:hover p {
                text-shadow: 0 0 5px #ffffff, 0 0 15px #ff0055, 0 0 25px #ff0055 !important;
            }
            </style>
            """, unsafe_allow_html=True)

        st.write("---")
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
                        "image_path": f"assets/캐릭터.gnp/{st.session_state.selected_avatar}"
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
        def render_kakaotalk_msg(role, content, char_name="", image_path=""):
            # HTML 특수문자 처리가 필요할 수 있으나 기본적으로 content 내 태그 허용
            content_html = content.replace('\\n', '<br>')
            if role == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
                    <div style="background-color: rgba(255, 0, 0, 0.6); color: #ffffff; padding: 10px 15px; border-radius: 15px 0 15px 15px; max-width: 70%; word-break: break-word; font-size: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                        {content_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 아바타 이미지 처리
                avatar_html = "👤"
                if image_path:
                    abs_img_path = os.path.join(BASE_DIR, image_path)
                    if os.path.exists(abs_img_path):
                        with open(abs_img_path, "rb") as img_file:
                            encoded_string = base64.b64encode(img_file.read()).decode()
                        avatar_html = f"<img src='data:image/png;base64,{encoded_string}' style='width: 100%; height: 100%; border-radius: 50%; object-fit: cover;'>"
                        
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 15px; align-items: flex-start;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #E2E2E2; margin-right: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; overflow: hidden;">
                        {avatar_html}
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
            render_kakaotalk_msg(msg["role"], msg["content"], char_data['name'], char_data.get('image_path', ''))
                
        if prompt := st.chat_input("메시지를 입력하세요..."):
            # 유저 메시지 표시
            render_kakaotalk_msg("user", prompt)
            
            with st.spinner("답변을 고민 중입니다..."):
                response = process_chat(prompt, char_id, char_data)
            
            if response:
                render_kakaotalk_msg("assistant", response, char_data['name'], char_data.get('image_path', ''))
            else:
                st.error("앗, 챗봇이 대답을 하지 못했어요. API 키나 네트워크 상태를 확인해주세요!")
