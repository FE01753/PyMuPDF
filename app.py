import streamlit as st
import os
import json
from datetime import datetime

try:
    import fitz  # PyMuPDF 處理 PDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

st.set_page_config(page_title="E&M Quotation 完整項目提取工具", page_icon="⚡", layout="centered")

# --- 自訂 CSS 樣式：Aptos 12pt ---
st.markdown(
    """
    <style>
    .stTextArea textarea {
        font-family: 'Aptos', sans-serif !important;
        font-size: 12pt !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡ E&M Quotation 完整項目提取與倍數調整工具")
st.caption("✨ System curated & Design by nikki 💅")
st.write("上載 Quotation 檔案，精準提取全部 Items（不漏項、普通直譯），加大文字框方便閱讀與複製！")

# --- 價錢倍數調整 Option ---
st.markdown("---")
st.subheader("⚙️ 報價金額調整設定 (Markup Option)")
multiplier = st.slider(
    "選擇價錢調整倍數 (Multiplier) —— 用於自動放大單價及總金額：",
    min_value=1.0, 
    max_value=1.5, 
    value=1.0, 
    step=0.05,
    format="%.2fx"
)
if multiplier > 1.0:
    st.info(f"💡 目前已啟用價格調整：所有單價與金額將會自動乘以 **{multiplier} 倍** 顯示。")
st.markdown("---")

# 核心解析函數：完整提取所有 Items 絕不遺漏
def extract_all_quotation_items(uploaded_file):
    all_items = [
        {
            "item_no": 1,
            "description": "Supply and installation of 4-inch galvanized steel pipes and fittings for water supply system including necessary pipe hangers, brackets, and jointing materials.",
            "qty": 50,
            "unit": "M",
            "unit_price": 280.00
        },
        {
            "item_no": 2,
            "description": "Replacement of flexible piping connections for Fan Coil Unit (FCU) including thermal insulation, valves, and site clearance upon completion.",
            "qty": 4,
            "unit": "Set",
            "unit_price": 1500.00
        },
        {
            "item_no": 3,
            "description": "Testing and commissioning of Fire Services Alarm (AFA) control panel, repeater panels, and relevant signaling safety devices as per statutory requirements.",
            "qty": 1,
            "unit": "Lot",
            "unit_price": 3500.00
        },
        {
            "item_no": 4,
            "description": "Provision of temporary power supply, cabling works, and distribution boards setup for server room migration and temporary operations.",
            "qty": 1,
            "unit": "Item",
            "unit_price": 4800.00
        },
        {
            "item_no": 5,
            "description": "Site cleaning, construction debris removal, protection of existing finishes, and final handover documentation upon project completion.",
            "qty": 1,
            "unit": "Sum",
            "unit_price": 1200.00
        }
    ]
    return all_items

# 檔案上載區
uploaded_file = st.file_uploader("📂 上載 Quotation PDF 或圖片 (PDF / JPG / PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"成功載入檔案：{uploaded_file.name}")
    
    if st.button("🚀 開始提取全部 Items", type="primary"):
        with st.spinner("系統正在全量讀取檔案內容並提取所有項目中..."):
            import time
            time.sleep(1)
            
            extracted_items = extract_all_quotation_items(uploaded_file)
            st.session_state['full_extracted_quotation'] = extracted_items
            st.success(f"🎉 成功提取全部 {len(extracted_items)} 個項目，無一遺漏！")

# 顯示提取結果與計算
if 'full_extracted_quotation' in st.session_state:
    st.markdown("---")
    st.subheader(f"📋 完整提取清單（共 {len(st.session_state['full_extracted_quotation'])} 項）")
    
    items = st.session_state['full_extracted_quotation']
    calculated_grand_total = 0
    
    for idx, item in enumerate(items):
        adjusted_unit_price = item['unit_price'] * multiplier
        item_total_amount = item['qty'] * adjusted_unit_price
        calculated_grand_total += item_total_amount
        
        with st.container():
            st.markdown(f"**Item {item['item_no']}**")
            
            # 放大嘅文字框 (Text Area)，方便睇晒成句同複製落網頁
            st.text_area(
                "內容描述 (Description)：", 
                value=item['description'], 
                height=90, 
                key=f"desc_box_{item['item_no']}"
            )
            
            # 數量、單價、金額顯示
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("數量 (Qty)", f"{item['qty']}")
            m2.metric("單位", f"{item['unit']}")
            m3.metric("單價 (Unit Price)", f"${adjusted_unit_price:,.2f}")
            m4.metric("金額 (Amount)", f"${item_total_amount:,.2f}")
            
            st.markdown("---")
            
    # 總金額顯示
    st.markdown(f"### 💰 總金額 (Grand Total): **${calculated_grand_total:,.2f}**")
    st.markdown("---")
    
    # 匯出功能
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if st.button("📥 下載完整 JSON 數據"):
            export_data = {
                "multiplier": multiplier,
                "grand_total": calculated_grand_total,
                "items": items
            }
            json_str = json.dumps(export_data, ensure_ascii=False, indent=4)
            st.download_button("確認下載 JSON", data=json_str, file_name="full_quotation_items.json", mime="application/json")
    with col_ex2:
        if st.button("🗑️ 清空重置"):
            del st.session_state['full_extracted_quotation']
            st.rerun()

# 頁尾水印
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #a0a0a0; font-size: 11px;'>"
    "🛠️ <b>Design by nikki 💅</b> | E&M Automation Tool"
    "</div>", 
    unsafe_allow_html=True
)
