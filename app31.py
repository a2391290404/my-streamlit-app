# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from fpdf import FPDF
import io

font_path = "SimHei.ttf"  
prop = fm.FontProperties(fname=font_path)

st.title("CSV 数据分析与可视化 - 按 target 划分数据集")

uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    target_col = 'target'

    if target_col not in df.columns:
        st.write(f"CSV 文件中没有找到 '{target_col}' 列，请检查文件内容。")
    else:
        group1 = df[df[target_col] == 1].drop(columns=[target_col])
        group2 = df[df[target_col] != 1].drop(columns=[target_col])

        st.write(f"target == 1 的样本数: {len(group1)}")
        st.write(f"target != 1 的样本数: {len(group2)}")

        total_samples = len(group1) + len(group2)
        if total_samples != 200000:
            st.write(f"警告：数据集样本总数不是 200,000 条，而是 {total_samples} 条。请检查数据集是否正确。")
        else:
            mean_diff = abs(group1.mean() - group2.mean())
            top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

            st.write("差异最大的列及其差异值：")
            st.write(top_diff_columns)

            st.write("差异最大的几列的分布对比（直方图）：")
            chart_images = []
            for col in top_diff_columns.index:
                st.write(f"列: {col}")

                col_range = (min(group1[col].min(), group2[col].min()), max(group1[col].max(), group2[col].max()))
                bin_count = 15

                fig, ax = plt.subplots()
                ax.hist(group1[col], bins=bin_count, alpha=0.5, label='target == 1', color='#4c72b0', range=col_range, density=True)
                ax.hist(group2[col], bins=bin_count, alpha=0.5, label='target != 1', color='#dd8452', range=col_range, density=True)

                ax.set_title(f'{col} 分布对比', fontproperties=prop, fontsize=14)
                ax.set_ylabel('频率', fontproperties=prop, fontsize=12)
                ax.set_xlabel('值', fontproperties=prop, fontsize=12)
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(fontsize=10)
                plt.yticks(fontsize=10)

                st.pyplot(fig)

                img = io.BytesIO()
                fig.savefig(img, format='png')
                img.seek(0)
                chart_images.append(img)

            if st.button('生成 PDF 报告'):
                pdf = FPDF()
                pdf.add_page()

                pdf.add_font("SimHei", "", "SimHei.ttf", uni=True)
                pdf.set_font("SimHei", size=12)

                pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
                pdf.ln(10)

                pdf.multi_cell(0, 10, txt=(
                    f"数据集样本总数: {total_samples}\n"
                    f"target == 1 的样本数: {len(group1)}\n"
                    f"target != 1 的样本数: {len(group2)}"
                ))
                pdf.ln(10)

                pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True, align='L')
                for col, diff in top_diff_columns.items():
                    pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True, align='L')
                pdf.ln(10)

                pdf.cell(200, 10, txt="图表可视化：", ln=True, align='L')
                for idx, img in enumerate(chart_images):
                    pdf.cell(200, 10, txt=f"图表 {idx+1}: {top_diff_columns.index[idx]} 的分布对比", ln=True, align='L')
                    pdf.image(img, x=10, y=None, w=190)
                    pdf.ln(10)

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
    st.write("请上传 CSV 文件。")



