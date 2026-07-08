import streamlit as st
import google.generativeai as genai
import gspread
import random

# --- 1. 初始化與 API 設定 ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 提升創意與隨機性的參數設定
generation_config = genai.types.GenerationConfig(
    temperature=0.9,
    top_p=0.95,
)
model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)

# --- 2. 連線至 Google Sheet ---
@st.cache_resource(ttl=600) # 快取 10 分鐘避免頻繁讀取
def load_sheet_data():
    # 透過 Streamlit Secrets 讀取金鑰並連線
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    
    # ⚠️ 請將下方的網址替換成您的 Google Sheet 真實網址 ⚠️
    sheet_url = "https://docs.google.com/spreadsheets/d/1FRYCNtjHpR6acyoLqf_KCzckFj-FYuOiYBkMtvBfLxk/edit?gid=0#gid=0" 
    sh = gc.open_by_url(sheet_url)
    worksheet = sh.sheet1
    
    # 抓取所有資料（包含標題列）
    data = worksheet.get_all_values()
    return data

# 讀取試算表資料
sheet_data = load_sheet_data()
# 剔除第一列標題，剩下純資料
records = sheet_data[1:] 

# 建立 A 欄（大項分類）的選單清單
category_options = [row[0] for row in records if row[0] != ""]

# --- 3. 介面設計：動態控制面板 ---
st.title("🎯 PTT 醫美口碑狙擊系統 (AIO 實體連動版)")

st.sidebar.header("戰略設定")
selected_category = st.sidebar.selectbox("步驟一：選擇本次任務主軸", category_options)
num_posts = st.sidebar.number_input("步驟二：生成篇數", min_value=1, max_value=5, value=1)

# 找出使用者選擇的那一列戰略資料
selected_row = next(row for row in records if row[0] == selected_category)
# 對應欄位解析
core_instruments = selected_row[1] # B 欄: 儀器與俗稱
core_pain_points = selected_row[2] # C 欄: 痛點與困擾
banned_words = selected_row[4]     # E 欄: 專屬禁語

# --- 4. 生成按鈕與三色骰子邏輯 ---
if st.button("🚀 啟動生成"):
    for i in range(num_posts):
        with st.spinner(f"正在為您編寫第 {i+1} 篇實戰文章..."):
            
            # 【🎲 三色骰子：AI 內部隨機拉霸機制】
            prompt = f"""
            你現在是一位真實的台灣 PTT facelift (醫美版) 鄉民。
            請根據以下「戰略參數」與「隨機骰子」，產出 1 篇具備強烈真實感的貼文，以及底下附帶的 10 則推文。

            【戰略參數】
            - 任務主軸：{selected_category}
            - 必須隨機挑選 1~2 個穿插的儀器/俗稱：{core_instruments}
            - 必須隨機挑選 1~2 個抱怨的核心痛點：{core_pain_points}

            【🎲 隨機劇本生成指令】(請每次都從以下三個維度隨機選擇一種風格來撰寫)
            1. 隨機題型：(A) 兩台儀器比較求薦、(B) 單純痛點求解答、(C) 單一儀器細節探討。
            2. 隨機情境：(A) 剛拿獎金預算有限、(B) 重大聚會前急救、(C) 被身邊人無意間嫌老、(D) 朋友打完被生火但怕痛、(E) 滑舊照產生嚴重焦慮。
            3. 推文風向：(A) 兩派擁護者戰翻、(B) 理性分析派科普、(C) 滅火酸民與護航派交戰。

            【PTT 專屬排版與格式限制 (違反即失敗)】
            1. 主文格式：這是在 PTT 發文，請強制使用手動斷行（Line-break），不要寫成長篇大論的段落，維持 BBS 的閱讀節奏。
            2. 推文格式：推文請維持獨立的邏輯結構（推、噓、→），並適當使用半形空格斷句。
            3. 字數控制：主文控制在 250 - 350 字以內，不宜過長。推文必須剛好 10 則。
            4. 絕對禁語：{banned_words}。禁止在文中出現「潛水很久」、「大大」、「大家好」等刻板用語。
            """

            response = model.generate_content(prompt)
            st.markdown(f"### 第 {i+1} 篇")
            st.write(response.text)
            st.markdown("---")
    st.success("✅ 任務執行完畢！")
