# %%
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import io

st.title("CSV 数据分析与可视化 - 按 target 分组")
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    target_col = df.columns[0]

    target_groups = df.groupby(target_col)
    unique_targets = df[target_col].unique()
    
    if len(unique_targets) != 2:
        st.write(f"数据中的 target 列应仅包含两类，但包含了这些值：{unique_targets}")
    else:

        group1 = target_groups.get_group(unique_targets[0]).drop(columns=[target_col])
        group2 = target_groups.get_group(unique_targets[1]).drop(columns=[target_col])

        mean_diff = abs(group1.mean() - group2.mean())

        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        if st.button('生成 PDF 报告'):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="数据分析报告", ln=True, align="C")

            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"列: {col}, 差异: {diff:.4f}", ln=True)

            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            st.download_button(
                label="下载 PDF 报告",
                data=pdf_output,
                file_name="data_analysis_report.pdf",
                mime="application/pdf"
            )



