import streamlit as st
import os
import json
from datetime import datetime

# 檢查有無裝好相關套件
try:
    import fitz  # PyMuPDF 用黎處理 PDF 轉圖片
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

st.set_page_config(page_title="E&M Quotation Item 智能提取工具", page_icon="⚡", layout="centered")

st.title("⚡ E&M Quotation 項目智能提取與英文轉化工具")
st.caption("✨ System curated & Design by nikki 💅")
st.write("上載 Quotation PDF 或圖片，AI 自動幫你拆解項目並轉化為專業英文，方便逐個 Item 複製落公司網頁！")

# 模擬 AI 拆解同翻譯功能 (實際應用時可以接通 API 或者用規則解析)
def mock_ai_extract_items(file_name):
    # 呢度模擬當你上載檔案後，AI 幫你抽出黎嘅工程 Items
    sample_items = [
        {
            "item_no": 1,
            "chinese_desc": "供應及安裝 4寸 鍍鋅鋼喉及相關配件",
            "english_desc": "Supply and installation of 4-inch galvanized steel pipes and associated fittings for water supply system.",
            "category": "Plumbing & Drainage"
        },
        {
            "item_no": 2,
            "chinese_desc": "更換冷氣機風機盤管 (FCU) 連接喉管",
            "english_desc": "Replacement of flexible piping connections for Fan Coil Unit (FCU) including insulation works.",
            "category": "Air Conditioning (HVAC)"
        },
        {
            "item_no": 3,
            "chinese_desc": "檢查及測試消防系統警報掣 (AFA Panel)",
            "english_desc": "Testing and commissioning of Fire Services Alarm (AFA) control panel and related signaling devices.",
            "category": "Fire Services (FS)"
        }
    ]
    return sample_items

# 上載區
uploaded_file = st.file_uploader("📂 上載 Quotation PDF 或工程圖片 (JPG/PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"成功載入檔案：{uploaded_file.name}")
    
    if st.button("🚀 開始 AI 智能提取與英文轉化", type="primary"):
        with st.spinner("AI 正在分析文件結構、提取 Item 並翻譯成專業英文..."):
            # 模擬處理時間
            import time
            time.sleep(1.5)
            
            extracted_items = mock_ai_extract_items(uploaded_file.name)
            st.session_state['extracted_items'] = extracted_items
            st.success(f"🎉 成功提取 {len(extracted_items)} 個工程項目！")

# 如果已經有提取結果，展示互動列表
if 'extracted_items' in st.session_state:
    st.markdown("---")
    st.subheader("📋 提取結果預覽（可逐個 Item 複製）")
    
    for idx, item in enumerate(st.session_state['extracted_items']):
        with st.container():
            st.markdown(f"**Item {item['item_no']} | 分類：{item['category']}**")
            
            col1, col2 = st.columns([5, 1])
            with col1:
                # 顯示英文版本（網頁用）同中文對照
                display_text = f"[{item['category']}] {item['english_desc']}"
                st.code(display_text, language="text")
            with col2:
                st.write("")
                # 提示
                st.caption("✨ 準備就緒")
            
            st.markdown(f"<span style='color: #666; font-size: 13px;'>原中文對照：{item['chinese_desc']}</span>", unsafe_allow_html=True)
            st.markdown("---")
            
    # 批量匯出功能
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if st.button("📥 下載所有 Items (JSON 格式)"):
            json_str = json.dumps(st.session_state['extracted_items'], ensure_ascii=False, indent=4)
            st.download_button("確認下載 JSON", data=json_str, file_name="website_items.json", mime="application/json")
    with col_ex2:
        if st.button("🗑️ 清空重置"):
            del st.session_state['extracted_items']
            st.rerun()

# 頁尾水印
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #a0a0a0; font-size: 11px;'>"
    "🛠️ <b>Design by nikki 💅</b> | E&M Automation Tool"
    "</div>", 
    unsafe_allow_html=True
)
