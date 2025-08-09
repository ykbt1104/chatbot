# ===== 最初に page_config を呼ぶ（最初の Streamlit コマンド）=====
import streamlit as st
st.set_page_config(page_title="Company Inner Search App")
# ===============================================================

# ===== Cloud/ローカル両対応のAPIキー読込 =====
import os
from dotenv import load_dotenv

load_dotenv()  # ローカル用 .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY が設定されていません（Secrets または .env）")
    st.stop()
# ============================================

"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

# ここから他モジュールを import（副作用があってももう安全）
import logging
import utils
from initialize import initialize
import components as cn
import constants as ct


############################################################
# 2. 設定関連
############################################################
# ※ set_page_config は最初に実行済みなのでここでは呼ばない
logger = logging.getLogger(ct.LOGGER_NAME)

############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)

############################################################
# 4. 初期表示
############################################################
# タイトル表示（ページタイトルは set_page_config、画面内タイトルは components 側で）
cn.display_app_title()

# モード表示
cn.display_select_mode()

# AIメッセージの初期表示
cn.display_initial_ai_message()

############################################################
# 5. 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

############################################################
# 6. チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)

############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    # 7-1. ユーザーメッセージの表示
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})
    with st.chat_message("user"):
        st.markdown(chat_message)

    # 7-2. LLMからの回答取得
    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    # 7-3. LLMからの回答表示
    with st.chat_message("assistant"):
        try:
            if st.session_state.mode == ct.ANSWER_MODE_1:
                content = cn.display_search_llm_response(llm_response)
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                content = cn.display_contact_llm_response(llm_response)
            else:
                content = ""
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    # 7-4. 会話ログへの追加
    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": content})
