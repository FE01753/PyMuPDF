import streamlit as st
import os
import json
from datetime import datetime

try:
    import fitz  # PyMuPDF 用黎處理 PDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

st.set_page_config(page_title="E&M Quotation 項目與金額智能提取系統", page_icon="⚡", layout="centered")

st.title("⚡ E&M Quotation 項目與金額智能提取系統")
st.caption("✨ System curated & Design by nikki 💅")
st.write("上載 PDF 或圖片，自動提取項目文字、數量、單價、金額及總金額，並支援自由調整價錢倍數！")

# --- 側邊欄或頂部：價錢倍數調整 Option ---
st.markdown("---")
st.subheader("⚙️ 報價金額調整設定 (Markup Option)")
multiplier = st.slider(
    "選擇價錢調整倍數 (Multiplier) —— 用於自動放大單價及金額：",
    min_value=1.0, 
    max_value=2.0, 
    value=1.0, 
    step=0.05,
    format="%.2fx"
)
if multiplier > 1.0:
    st.info(f"💡 目前已啟用價格調整：所有單價與金額將會自動乘以 **{multiplier} 倍** 顯示。")
st.markdown("---")

# 模擬真實提取出嚟嘅工程項目清單（含數量、單價、金額）
def mock_extract_quotation_data(file_name):
    # 呢度模擬從 PDF/圖片中解析出嚟嘅原始數據
    raw_items = [
        {
            "item_no": 1,
            "description": "Supply and installation of 4-inch galvanized steel pipes and fittings",
            "qty": 50,
            "unit": "M",
            "unit_price": 280.00
        },
        {
            "item_no": 2,
            "description": "Replacement of Fan Coil Unit (FCU) connection piping and insulation",
            "qty": 4,
            "item": "Set",
            "unit_price": 1500.00
        },
        {
            "item_no": 3,
            "description": "Testing and commissioning of AFA control panel and safety devices",
            "qty": 1,
            "item": "Lot",
            "unit_price": 3500.00
        }
    ]
    return raw_items

# 檔案上載區
uploaded_file = st.file_uploader("📂 上載 Quotation PDF 或工程圖片 (PDF / JPG / PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"成功載入檔案：{uploaded_file.name}")
    
    if st.button("🚀 開始提取文字與金額", type="primary"):
        with st.spinner("AI 正在深度解析文件內容、數量及金額中..."):
            import time
            time.sleep(1)
            
            extracted_data = mock_extract_quotation_data(uploaded_file.name)
            st.session_state['extracted_quotation'] = extracted_data
            st.success("🎉 提取成功！")

# 顯示提取結果與計算
if 'extracted_quotation' in st.session_state:
    st.markdown("---")
    st.subheader("📋 提取結果與金額試算")
    
    items = st.session_state['extracted_quotation']
    
    calculated_grand_total = 0
    
    for idx, item in enumerate(items):
        # 計算調整後嘅單價同總金額
        adjusted_unit_price = item['unit_price'] * multiplier
        item_total_amount = item['qty'] * adjusted_unit_price
        calculated_grand_total += item_total_amount
        
        with st.container():
            st.markdown(f"**Item {item['item_no']}**")
            
            # 顯示描述文字（方便直接 Copy 落網頁）
            col_text, col_copy = st.columns([5, 1])
            with col_text:
                st.code(item['description'], language="text")
            with col_copy:
                st.write("")
                st.caption("✨ 準備就緒")
            
            # 數量、單價、金額顯示
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("數量 (Qty)", f"{item['qty']}")
            m2.metric("單位", f"{item.get('item', item.get('unit', 'Pcs'))}")
            m3.metric("單價 (Unit Price)", f"${adjusted_unit_price:,.2f}")
            m4.metric("金額 (Amount)", f"${item_total_amount:,.2f}")
            
            st.markdown("---")
            
    # 總金額顯示
    st.markdown(f"### 💰 總金額 (Grand Total): **${calculated_grand_total:,.2f}**")
    st.markdown("---")
    
    # 匯出功能
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if st.button("📥 下載帶有倍數嘅 JSON 數據"):
            export_data = {
                "multiplier": multiplier,
                "grand_total": calculated_grand_total,
                "items": items
            }
            json_str = json.dumps(export_data, ensure_ascii=False, indent=4)
            st.download_button("確認下載 JSON", data=json_str, file_name="quotation_extracted_items.json", mime="application/json")
    with col_ex2:
        if st.button("🗑️ 清空重置"):
            del st.session_state['extracted_quotation']
            st.rerun()

# 頁尾水印
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #a0a0a0; font-size: 11px;'>"
    "🛠️ <b>Design by nikki 💅</b> | E&M Automation Tool"
    "</div>", 
    unsafe_allow_html=True
)
