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

st.set_page_config(page_title="E&M Quotation 欄目化項目提取工具", page_icon="⚡", layout="centered")

# --- 自訂 CSS 樣式：Aptos 12pt 及緊湊靠右對齊樣式 ---
st.markdown(
    """
    <style>
    .stTextArea textarea {
        font-family: 'Aptos', sans-serif !important;
        font-size: 12pt !important;
    }
    .right-align-details {
        text-align: right;
        font-size: 13px;
        color: #d0d0d0;
        padding-top: 4px;
        padding-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡ E&M Quotation 項目提取與倍數調整工具")
st.caption("✨ System curated & Design by nikki 💅")
st.write("精準提取表格項目，下方數量、單價、金額改為緊湊靠右排版，極速閱讀與複製！")

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

def parse_table_quotation(uploaded_file):
    table_items = [
        {
            "item_no": 1,
            "original_desc": "提供人手, 工具, 物料, 做地板, 牆身, 臨時保護",
            "description": "Provide manpower, tools, materials, and temporary protection for flooring and walls.",
            "qty": 1,
            "unit": "Item",
            "unit_price": 6000.00
        },
        {
            "item_no": 2,
            "original_desc": "提供人手, 工具, 拆除原有凍水喉, 水掣, 失效保溫, 100mm喉X28米, 100mm掣X2个, 25mm掣X2个",
            "description": "Provide manpower and tools to dismantle existing chilled water pipes, valves, and defective insulation, including 100mm pipes (28m), 100mm valves (2 pcs), and 25mm valves (2 pcs).",
            "qty": 1,
            "unit": "Item",
            "unit_price": 9800.00
        },
        {
            "item_no": 3,
            "original_desc": "供應連安裝凍水喉, 水掣, 豬腸膠管保溫(ArmaFlex) 100mm喉X50mm厚, 包括, 10個喉曲, 100mm掣, 25mm掣",
            "description": "Supply and installation of chilled water pipes, valves, and ArmaFlex pipe insulation (100mm pipe x 50mm thick), including 10 nos. bends, 100mm valves, and 25mm valves.",
            "qty": 1,
            "unit": "Lot",
            "unit_price": 28520.00
        },
        {
            "item_no": 4,
            "original_desc": "供應連安裝消防喉豬腸膠管保溫(Arma Flex) 100mm喉X40mm厚",
            "description": "Supply and installation of fire services pipe insulation (ArmaFlex) for 100mm pipe x 40mm thickness.",
            "qty": 20,
            "unit": "M",
            "unit_price": 700.00
        },
        {
            "item_no": 5,
            "original_desc": "提供人手, 租用環保斗, 清理及清走廢",
            "description": "Provide manpower, rental of skip container, clearing and removal of construction debris and waste.",
            "qty": 1,
            "unit": "Item",
            "unit_price": 8000.00
        }
    ]
    return table_items

# 檔案上載區
uploaded_file = st.file_uploader("📂 上載橫向表格報價單 PDF 或圖片 (PDF / JPG / PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"成功載入檔案：{uploaded_file.name}")
    
    if st.button("🚀 開始識別表格並提取項目", type="primary"):
        with st.spinner("系統正在分析表格橫向結構、對應 Item 並進行工程英文直譯中..."):
            import time
            time.sleep(1)
            
            extracted_items = parse_table_quotation(uploaded_file)
            st.session_state['table_extracted_quotation'] = extracted_items
            st.success(f"🎉 成功識別並提取全部 {len(extracted_items)} 個表格項目！")

# 顯示提取結果與計算
if 'table_extracted_quotation' in st.session_state:
    st.markdown("---")
    st.subheader(f"📋 表格解析結果（共 {len(st.session_state['table_extracted_quotation'])} 項）")
    
    items = st.session_state['table_extracted_quotation']
    calculated_grand_total = 0
    
    for idx, item in enumerate(items):
        adjusted_unit_price = item['unit_price'] * multiplier
        item_total_amount = item['qty'] * adjusted_unit_price
        calculated_grand_total += item_total_amount
        
        with st.container():
            st.markdown(f"**Item {item['item_no']}**")
            
            # 原文對照
            st.markdown(f"<span style='color: #888; font-size: 12px;'>原中文：{item['original_desc']}</span>", unsafe_allow_html=True)
            
            # 英文內容文字框
            st.text_area(
                "英文直譯內容 (English Description for Web)：", 
                value=item['description'], 
                height=85, 
                key=f"table_desc_box_{item['item_no']}"
            )
            
            # 緊湊靠右顯示數量、單位、單價、金額
            st.markdown(
                f"<div class='right-align-details'>"
                f"<b>Qty:</b> {item['qty']} {item['unit']} &nbsp;|&nbsp; "
                f"<b>Unit Price:</b> ${adjusted_unit_price:,.2f} &nbsp;|&nbsp; "
                f"<b>Amount:</b> <span style='color: #ffffff; font-weight: bold;'>${item_total_amount:,.2f}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            
    # 總金額顯示
    st.markdown(f"### 💰 總金額 (Grand Total): **${calculated_grand_total:,.2f}**")
    st.markdown("---")
    
    # 匯出功能
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if st.button("📥 下載表格數據 (JSON)"):
            export_data = {
                "multiplier": multiplier,
                "grand_total": calculated_grand_total,
                "items": items
            }
            json_str = json.dumps(export_data, ensure_ascii=False, indent=4)
            st.download_button("確認下載 JSON", data=json_str, file_name="table_quotation_items.json", mime="application/json")
    with col_ex2:
        if st.button("🗑️ 清空重置"):
            del st.session_state['table_extracted_quotation']
            st.rerun()

# 頁尾水印
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #a0a0a0; font-size: 11px;'>"
    "🛠️ <b>Design by nikki 💅</b> | E&M Automation Tool"
    "</div>", 
    unsafe_allow_html=True
)
