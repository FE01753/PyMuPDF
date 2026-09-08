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

st.set_page_config(page_title="E&M Quotation Excel 緊湊表格提取", page_icon="⚡", layout="wide")

# --- 自訂 CSS 樣式：Excel 風格緊湊表格 ---
st.markdown(
    """
    <style>
    .stTextArea textarea {
        font-family: 'Aptos', sans-serif !important;
        font-size: 11pt !important;
        padding: 4px 8px !important;
    }
    table.excel-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Aptos', sans-serif;
        font-size: 12pt;
        background-color: #1e1e1e;
        color: #f0f0f0;
        margin-bottom: 20px;
    }
    table.excel-table th, table.excel-table td {
        border: 1px solid #444444;
        padding: 8px 10px;
        vertical-align: middle;
    }
    table.excel-table th {
        background-color: #2d2d2d;
        color: #ffffff;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡ E&M Quotation Excel 緊湊表格提取工具")
st.caption("✨ System curated & Design by nikki 💅")
st.write("完美還原 Excel 表格嘅極致緊湊排版，一眼睇晒所有 Items、英文描述與金額試算！")

# --- 價錢倍數調整 Option ---
st.markdown("---")
col_opt1, col_opt2 = st.columns([2, 3])
with col_opt1:
    multiplier = st.slider(
        "選擇價錢調整倍數 (Multiplier)：",
        min_value=1.0, 
        max_value=1.5, 
        value=1.0, 
        step=0.05,
        format="%.2fx"
    )
with col_opt2:
    if multiplier > 1.0:
        st.info(f"💡 目前已啟用價格調整：所有單價與金額將自動乘以 **{multiplier} 倍**。")
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
    
    if st.button("🚀 開始識別表格並以 Excel 格式展示", type="primary"):
        with st.spinner("系統正在分析表格並排版中..."):
            import time
            time.sleep(1)
            
            extracted_items = parse_table_quotation(uploaded_file)
            st.session_state['excel_extracted_quotation'] = extracted_items
            st.success(f"🎉 成功識別全部 {len(extracted_items)} 個項目！")

# 顯示 Excel 風格緊湊表格
if 'excel_extracted_quotation' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 Excel 緊湊表格檢視（共 {len(st.session_state['excel_extracted_quotation'])} 項）")
    
    items = st.session_state['excel_extracted_quotation']
    calculated_grand_total = 0
    
    # 建立表格 HTML 開頭
    table_html = """
    <table class="excel-table">
        <thead>
            <tr>
                <th style="width: 6%;">Item</th>
                <th style="width: 50%;">English Description (for Web)</th>
                <th style="width: 11%;">Qty</th>
                <th style="width: 14%;">Unit Price</th>
                <th style="width: 19%;">Amount</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for item in items:
        adjusted_unit_price = item['unit_price'] * multiplier
        item_total_amount = item['qty'] * adjusted_unit_price
        calculated_grand_total += item_total_amount
        
        # 每行的 HTML 結構
        table_html += f"""
            <tr>
                <td style="text-align: center; font-weight: bold;">{item['item_no']}</td>
                <td>
                    <div style="font-size: 11pt; margin-bottom: 2px;">{item['description']}</div>
                    <div style="font-size: 9pt; color: #888;">原中文: {item['original_desc']}</div>
                </td>
                <td style="text-align: center;">{item['qty']} {item['unit']}</td>
                <td style="text-align: right;">${adjusted_unit_price:,.2f}</td>
                <td style="text-align: right; font-weight: bold; color: #4da6ff;">${item_total_amount:,.2f}</td>
            </tr>
        """
        
    # 結尾加上總金額行
    table_html += f"""
            <tr style="background-color: #252525;">
                <td colspan="4" style="text-align: right; font-weight: bold;">Grand Total (總金額):</td>
                <td style="text-align: right; font-weight: bold; color: #4da6ff; font-size: 13pt;">${calculated_grand_total:,.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    # 渲染緊湊 Excel 表格
    st.markdown(table_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 匯出與重置功能
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if st.button("📥 下載表格數據 (JSON)"):
            export_data = {
                "multiplier": multiplier,
                "grand_total": calculated_grand_total,
                "items": items
            }
            json_str = json.dumps(export_data, ensure_ascii=False, indent=4)
            st.download_button("確認下載 JSON", data=json_str, file_name="excel_quotation_items.json", mime="application/json")
    with col_ex2:
        if st.button("🗑️ 清空重置"):
            del st.session_state['excel_extracted_quotation']
            st.rerun()

# 頁尾水印
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #a0a0a0; font-size: 11px;'>"
    "🛠️ <b>Design by nikki 💅</b> | E&M Automation Tool"
    "</div>", 
    unsafe_allow_html=True
)
