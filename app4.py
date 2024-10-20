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

    unique_targets = df[target_col].unique()
    
    st.write(f"Target 列中的唯一值：{unique_targets}")

    if len(unique_targets) < 2:
        st.write("数据中的 target 列应包含至少两个不同的类。")
    else:

        target1 = st.selectbox("选择第一个类", unique_targets)
        target2 = st.selectbox("选择第二个类", unique_targets)

        if target1 != target2:

            group1 = df[df[target_col] == target1].drop(columns=[target_col])
            group2 = df[df[target_col] == target2].drop(columns=[target_col])

            mean_diff = abs(group1.mean() - group2.mean())

            top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

            st.write("差异最大的列及其差异值：")
            st.write(top_diff_columns)

            corr_group1 = group1.corr()
            corr_group2 = group2.corr()

            st.write(f"{target1} 类的相关性矩阵：")
            st.write(corr_group1)

            st.write(f"{target2} 类的相关性矩阵：")
            st.write(corr_group2)

            if st.button('生成 PDF 报告'):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="数据分析报告", ln=True, align="C")

                pdf.cell(200, 10, txt=f"比较的 target 类：{target1} 和 {target2}", ln=True)
                pdf.cell(200, 10, txt="差异最大的几列：", ln=True)
                for col, diff in top_diff_columns.items():
                    pdf.cell(200, 10, txt=f"列: {col}, 差异: {diff:.4f}", ln=True)
                
                pdf.cell(200, 10, txt=f"{target1} 类的相关性矩阵：", ln=True)
                for row in corr_group1.itertuples():
                    pdf.cell(200, 10, txt=str(row), ln=True)
                
                pdf.cell(200, 10, txt=f"{target2} 类的相关性矩阵：", ln=True)
                for row in corr_group2.itertuples():
                    pdf.cell(200, 10, txt=str(row), ln=True)

                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_output.seek(0)

                st.download_button(
                    label="下载 PDF 报告",
                    data=pdf_output,
                    file_name="data_analysis_report.pdf",
                    mime="application/pdf"
                )
        else:
            st.write("请选择两个不同的类进行比较。")



