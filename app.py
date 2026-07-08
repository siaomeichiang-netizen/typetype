import streamlit as st
import google.generativeai as genai
import gspread
import random

# --- 1. 初始化與 API 設定 ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

generation_config = genai.types.GenerationConfig(
    temperature=0.95,  # 提高隨機性，讓文體更發散
    top_p=0.95,
)
model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)

# --- 2. 連線至 Google Sheet ---
@st.cache_resource(ttl=600)
def load_sheet_data():
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    # ⚠️ 請確保下方的網址替換成您的 Google Sheet 真實網址
    sheet_url = "https://docs.google.com/spreadsheets/d/1FRYCNtjHpR6acyoLqf_KCzckFj-FYuOiYBkMtvBfLxk/edit?gid=0#gid=0" 
    sh = gc.open_by_url(sheet_url)
    worksheet = sh.sheet1
    return worksheet.get_all_values()

sheet_data = load_sheet_data()
records = sheet_data[1:] 
category_options = [row[0] for row in records if row[0] != ""]

# --- 3. 介面設計 ---
st.title("🎯 PTT 醫美口碑狙擊系統 (合規嚴格版)")

st.sidebar.header("戰略設定")
selected_category = st.sidebar.selectbox("步驟一：選擇本次任務主軸", category_options)
num_posts = st.sidebar.number_input("步驟二：生成篇數", min_value=1, max_value=5, value=1)

selected_row = next(row for row in records if row[0] == selected_category)
core_instruments = selected_row[1] 
core_pain_points = selected_row[2] 
banned_words = selected_row[4]     

# --- 4. 生成按鈕與嚴格規範邏輯 ---
if st.button("🚀 啟動生成"):
    # 【關鍵升級】：在迴圈外先將試算表的字串切成陣列
    inst_list = [x.strip() for x in core_instruments.split(',') if x.strip()]
    pain_list = [x.strip() for x in core_pain_points.split(',') if x.strip()]
    
    for i in range(num_posts):
        with st.spinner(f"正在編寫第 {i+1} 篇極致去味文案..."):
            
            # 【🎲 系統強制抽籤：收回 AI 選擇權】
            chosen_inst = random.choice(inst_list) if inst_list else core_instruments
            chosen_pain = random.choice(pain_list) if pain_list else core_pain_points
            
            # 題型大類骰子
            post_type = random.choice(["討論閒聊型", "心得分享型"])
            
            # 【🎲 第四顆骰子：排版風格引擎 (根據真實截圖建構)】
            layout_style = random.choice([
                "【短句留白型】：每講 1~2 句話就必須「空一行(留白)」。字數長短極度不一，看起來像在講話停頓，語氣隨性。",
                "【碎碎念連續型】：絕對不要有任何空白行！文字一塊到底，但每句話還是要手動換行。結尾必須加上「><」或「@@」等BBS表情符號。",
                "【段落分明型】：每 3~4 行組成一個區塊，區塊之間必須「空一行」。句子長短差異要很大，可以帶有「欸」、「啊」等語氣詞。"
            ])
            
            prompt = f"""
            你現在是一位真實的台灣 PTT facelift (醫美版) 鄉民。
            請根據以下「戰略參數」與嚴格的「內部作業規範」，產出 1 篇貼文與剛好 10 則推文。

            【戰略參數 (系統已強制鎖定，絕對不可偏題)】
            - 任務主軸：{selected_category}
            - 本次強制討論的儀器/俗稱：【 {chosen_inst} 】(嚴禁提及或比較其他任何同類儀器，整篇文章只能圍繞這個詞彙)
            - 本次強制抱怨的核心痛點：【 {chosen_pain} 】
            - 專屬禁語：{banned_words}

            【🎯 規則一：看板規則與字數死線 (二選一，由系統隨機抽中：【{post_type}】)】
            若抽中【討論閒聊型】：
              - 標題分類只能從 [問題]、[討論]、[閒聊] 這三個當中隨機選一個。
              - 主文內容（不含標題與推文）字數必須嚴格限制在 100 字以內，多一個字即視為失敗！
            若抽中【心得分享型】：
              - 標題分類只能從 [心得]、[分享] 這兩個當中隨機選一個。
              - 主文內容（不含標題與推文）字數必須嚴格限制在 300 字以內，多一個字即視為失敗！

            【🎯 規則二：隨機排版引擎強制套用】
            你本次被指定的發文排版風格為：{layout_style}
            請務必打破機器人式的工整對齊，讓句子有長有短，完美模擬該風格。

            【❌ 規則三：絕對死線（只要踩到任何一條，該文案即視為徹底失敗）】
            1. 嚴禁出現「鏡子」、「照鏡子」。請透過拍照、親友說、視訊畫面來表達老化。
            2. 嚴禁在文章內文使用「1. 2. 3.」等工整的條列式提問。
            3. 嚴禁使用「版友」（一律強制改成木字旁的「板友」）。
            4. 嚴禁出現「潛水很久」、「第一次發文」、「大家好」、「先謝謝大家」等客套公關用語。請直接隨性結尾（如：有解嗎？、求開導）。
            5. 嚴禁將中英文或多個俗稱合併使用！例如絕對不能寫出「鳳凰FLX」，只能單寫「鳳凰」或「FLX」。

            【📋 規則四：推文內部作業規範格式 (格式極度嚴格)】
            推文輸出格式嚴禁自創任何帳號、時間或 IP 位址。請完全依照以下規範輸出：
            - 原本為「推」的留言，強制改用「推|」開頭，後面直接接文字。
            - 原本為「噓」的留言，強制改用「噓|」開頭，後面直接接文字。
            - 原本為「→」箭頭的留言，不加任何開頭符號，直接輸出文字。
            每則留言必須獨立成行，總共必須剛好 10 則。

            【正確推文格式範例】
            推|打完真的有緊但荷包很痛
            噓|這台根本智商稅打完超無感
            痛感完全不是同個級別吧
            """

            response = model.generate_content(prompt)
            st.markdown(f"### 第 {i+1} 篇 (指定：{post_type} / {layout_style.split('：')[0]})")
            st.code(response.text, language="text") 
            st.markdown("---")
    st.success("✅ 所有合規文案任務執行完畢！")
