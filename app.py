import streamlit as st
import random
import google.generativeai as genai
import datetime
import re

# --- 基本設定與 API ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("系統維護中，請聯繫發包管理員。")
    st.stop()

# --- 基礎資料庫 ---
treatments = ["鳳凰電波900發", "海芙音波媚必提", "皮秒雷射(雙機蜂巢)"]

# 【需求 1】寫死發文的標題分類
post_types = ["問題", "分享", "心得", "討論", "閒聊"]

# --- UI 介面設計 ---
st.set_page_config(page_title="口碑任務生成系統", layout="centered")
st.title("📱 醫美口碑任務產生器")
st.markdown("請輸入您的專屬代號，點擊生成後，**務必下載檔案並回傳至群組**。")

worker_id = st.text_input("👤 請輸入您的打工仔代號 (必填，如 W01)", placeholder="例如: W01")

if worker_id:
    if st.button("🎲 抽取任務並生成完整腳本", type="primary", use_container_width=True):
        
        chosen_treatment = random.choice(treatments)
        chosen_type = random.choice(post_types)
        
        # 【需求 3】依據分類動態控制字數
        if chosen_type in ["問題", "討論", "閒聊"]:
            length_constraint = "開題內文請嚴格控制在 150 字以內，極度精簡。"
        else:
            length_constraint = "開題內文請嚴格控制在 350 字以內。"
        
        with st.spinner('機器人正在撰寫您的專屬任務腳本，請稍候約 10 秒...'):
            try:
                # 終極優化 Prompt 
                prompt = f"""
                你現在是一位真實的台灣 PTT facelift (醫美版) 鄉民。請根據以下設定撰寫貼文與 10 則推文。
                設定：發文類型為 [{chosen_type}]，主題關於 {chosen_treatment}。

                【標題與內文字數限制】
                1. 第一行只能輸出文章標題，格式為「[{chosen_type}] 標題描述」。
                2. 標題描述（不含前面的分類標籤）必須嚴格控制在 19 個字元以內！絕對不要太工整或結構完整，要展現口語化與隨性真實感（例如：「鳳凰電波900發 到底痛不痛」而非「想請益大家鳳凰電波900發痛感」）。
                3. {length_constraint}

                【排版與標點符號嚴格要求 (極度重要)】
                1. 絕對不要在文末輸出 PTT 的發信站與文章網址區塊 (例如：-- ※ 發信站...)，完全不要出現。
                2. 內文必須採用「手動換行」排版，模擬真實 BBS 介面的視覺斷句。
                3. 標點符號限制：全篇(包含內文與推文)絕對不要使用工整的全形標點符號（，。！？）來斷句。
                4. 你必須極大量使用「半形空格」來代替標點符號！空格斷句的比例必須佔全篇的 70% 以上。
                5. 模擬不同人的打字習慣，可隨性穿插少量的半形符號 (.,?!) 或全形符號。整體感覺要像用手機快速打字、懶得切換鍵盤的破碎感。

                【推文區格式嚴格限制】
                請直接輸出 10 則留言，格式必須完全遵守以下規定：
                - 絕對不要模擬推文的帳號與時間！
                - 如果是推，請直接輸出「推|留言內容」
                - 如果是噓，請直接輸出「噓|留言內容」
                - 如果是箭頭(一般留言)，請不需要加任何標示，直接輸出「留言內容」
                - 留言內容一樣要符合「大量空格斷句」的隨性風格，包含正負風向。
                """
                
                response = model.generate_content(prompt)
                script_content = response.text
                
                # --- 提取標題並處理檔名 ---
                lines = [line.strip() for line in script_content.split('\n') if line.strip()]
                raw_title = lines[0] if lines else "未命名腳本"
                safe_title = re.sub(r'[\\/*?:"<>|#]', '', raw_title).strip()
                date_str = datetime.datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_title}_{date_str}_{worker_id}.txt"
                
                # 檔案內部抬頭設計
                file_content = f"=========================================\n【執行人員】{worker_id}\n【生成時間】{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n【系統設定】{chosen_type} | {chosen_treatment}\n=========================================\n\n{script_content}\n"
                
                st.session_state['ready_file_name'] = file_name
                st.session_state['ready_file_content'] = file_content
                st.success("✅ 任務生成成功！請點擊下方按鈕下載檔案。")
                
            except Exception as e:
                st.error(f"生成失敗，請再試一次。錯誤訊息: {e}")

# --- 強制下載動線 ---
if 'ready_file_content' in st.session_state:
    st.markdown("---")
    st.download_button(
        label=f"📥 下載檔案：{st.session_state['ready_file_name']}",
        data=st.session_state['ready_file_content'],
        file_name=st.session_state['ready_file_name'],
        mime="text/plain",
        use_container_width=True
    )
