import streamlit as st
import random
import google.generativeai as genai
import datetime
import re

# --- 基本設定與 API ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error("系統維護中，請聯繫發包管理員。")
    st.stop()

# --- 基礎資料庫 ---
treatments = ["鳳凰電波900發", "海芙音波媚必提", "皮秒雷射(雙機蜂巢)"]
post_types = ["問題", "心得", "分享"]

# --- UI 介面設計 ---
st.set_page_config(page_title="口碑任務生成系統", layout="centered")
st.title("📱 醫美口碑任務產生器")
st.markdown("請輸入您的專屬代號，點擊生成後，**務必下載檔案並回傳至群組**。")

worker_id = st.text_input("👤 請輸入您的打工仔代號 (必填，如 W01)", placeholder="例如: W01")

if worker_id:
    if st.button("🎲 抽取任務並生成完整腳本", type="primary", use_container_width=True):
        
        chosen_treatment = random.choice(treatments)
        chosen_type = random.choice(post_types)
        
        with st.spinner('機器人正在撰寫您的專屬任務腳本，請稍候約 10 秒...'):
            try:
                # 【優化 Prompt：強制第一行為乾淨標題，並嚴格綁定 PTT 排版邏輯】
                prompt = f"""
                你現在是一位非常資深的台灣 PTT 鄉民，超級熟悉 PTT facelift (醫美版) 的生態與用語。
                請根據以下設定撰寫一篇逼真的貼文與 10 則推文。

                設定：發文類型為 [{chosen_type}]，主題關於 {chosen_treatment}。

                【輸出與排版嚴格要求】
                1. 第一行：絕對只能輸出文章標題，必須包含分類標籤 (如 [{chosen_type}])，不要加上任何 Markdown 符號 (如 ### 或 **)。
                2. 內文：主文請採用「手動換行」的排版方式（約每 30-40 個中文字元就換行），模擬真實 BBS 介面的視覺斷句，絕對不要出現冗長且沒有換行的文字方塊。
                3. 推文區：留言請維持當前系統邏輯結構，嚴格遵守 PTT 推文格式（推/→/噓 帳號: 留言內容 時間）。包含正負風向交織。
                """
                
                response = model.generate_content(prompt)
                script_content = response.text
                
                # --- 核心邏輯：提取標題並處理檔名 ---
                # 1. 將文章拆分成多行，抓取第一行（非空白行）作為標題
                lines = [line.strip() for line in script_content.split('\n') if line.strip()]
                raw_title = lines[0] if lines else "未命名腳本"
                
                # 2. 清除不能作為檔名的特殊字元 (\ / : * ? " < > |) 以及多餘的井字號
                safe_title = re.sub(r'[\\/*?:"<>|#]', '', raw_title).strip()
                
                # 3. 組合新檔名格式：標題_日期_人員名稱.txt
                date_str = datetime.datetime.now().strftime("%Y%m%d")
                file_name = f"{safe_title}_{date_str}_{worker_id}.txt"
                
                # 檔案內部抬頭設計
                file_content = f"""=========================================
【執行人員】{worker_id}
【生成時間】{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
【系統設定】{chosen_type} | {chosen_treatment}
=========================================

{script_content}
"""
                # 儲存到暫存區供下載按鈕使用
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
