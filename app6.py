# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

st.title("CSV 数据分析与可视化 - 按 target 分组")
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    
    target_col = df.columns[0]
    
    unique_targets = df[target_col].unique()
    st.write(f"Target 列中的唯一值: {unique_targets}")
    
    if len(unique_targets) != 2:
        st.write("数据中的 target 列应仅包含两类。")
    else:
        group1 = df[df[target_col] == unique_targets[0]].drop(columns=[target_col])
        group2 = df[df[target_col] == unique_targets[1]].drop(columns=[target_col])

        mean_diff = abs(group1.mean() - group2.mean())

        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        st.write("差异最大的几列的比较：")
        for col in top_diff_columns.index:
            st.write(f"列: {col}")
            st.line_chart(pd.DataFrame({
                f'Group {unique_targets[0]}': group1[col],
                f'Group {unique_targets[1]}': group2[col]
            }).reset_index(drop=True))

        st.write("差异最大的几列的相关性矩阵：")
        combined_groups = pd.concat([group1[top_diff_columns.index], group2[top_diff_columns.index]])
        corr_matrix = combined_groups.corr()
        st.write(corr_matrix)

        if st.button('生成 PDF 报告'):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
            pdf.cell(200, 10, txt="按 target 分组的差异分析", ln=True, align='C')

            pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True)
            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"{col}: {diff}", ln=True)

            pdf.cell(200, 10, txt="相关性矩阵：", ln=True)
            for row in corr_matrix.index:
                row_data = ', '.join([f"{val:.2f}" for val in corr_matrix.loc[row]])
                pdf.cell(200, 10, txt=f"{row}: {row_data}", ln=True)

            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            st.download_button(
                label="下载 PDF 报告",
                data=pdf_output,
                file_name="data_analysis_report.pdf",
                mime="application/pdf"
            )



