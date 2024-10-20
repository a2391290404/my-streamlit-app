# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os
from datetime import datetime

CODE_DIR = "code/"
REPORT_DIR = "reports/"

os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d")

st.title("CSV 数据分析与可视化 - 自动差异分析")

uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    target_col = df.columns[0]
    
    target_counts = df[target_col].value_counts()
    
    if len(target_counts) < 2:
        st.write("数据中的 target 列应至少包含两个不同的类。")
    else:
        selected_targets = target_counts.index[:2]
        st.write(f"自动选取的两个 target 类别为: {selected_targets[0]} 和 {selected_targets[1]}")

        group1 = df[df[target_col] == selected_targets[0]].drop(columns=[target_col])
        group2 = df[df[target_col] == selected_targets[1]].drop(columns=[target_col])

        mean_diff = abs(group1.mean() - group2.mean())

        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        st.write("差异最大的几列的比较：")
        fig_list = []
        for col in top_diff_columns.index:
            st.write(f"列: {col}")
            fig, ax = plt.subplots()
            ax.plot(group1[col], label=f'{selected_targets[0]}', color='blue')
            ax.plot(group2[col], label=f'{selected_targets[1]}', color='red')
            ax.set_title(f"Comparison of {col}")
            ax.legend()
            st.pyplot(fig)
            fig_list.append(fig)

        if st.button('生成 PDF 报告'):
            pdf = FPDF()
            pdf.add_page()

            pdf.add_font("SimHei", "", "SimHei.ttf", uni=True)
            pdf.set_font("SimHei", size=12)

            pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
            pdf.cell(200, 10, txt="按 target 分组的差异分析", ln=True, align='C')

            pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True)
            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True)

            for i, fig in enumerate(fig_list):
                img_path = f'{REPORT_DIR}plot_{i}.png'
                fig.savefig(img_path)
                pdf.image(img_path, x=10, y=None, w=180)

            pdf_output = io.BytesIO()
            pdf_name = f"{timestamp}-data_analysis_report.pdf"
            pdf.output(pdf_output, name=pdf_name)
            pdf_output.seek(0)

            st.download_button(
                label="下载 PDF 报告",
                data=pdf_output,
                file_name=pdf_name,
                mime="application/pdf"
            )



