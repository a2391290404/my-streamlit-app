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

        st.write("类别 1 和类别 2 的描述性统计：")
        st.write(f"类别 1 ({selected_targets[0]}) 的描述统计：")
        st.write(group1.describe())

        st.write(f"类别 2 ({selected_targets[1]}) 的描述统计：")
        st.write(group2.describe())

        mean_diff = abs(group1.mean() - group2.mean())
        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        st.write("差异最大的几列的比较（柱状图）：")
        chart_images = []
        for col in top_diff_columns.index:
            st.write(f"列: {col}")

            fig, ax = plt.subplots()
            bars = ax.bar([f'{selected_targets[0]}', f'{selected_targets[1]}'],
                          [group1[col].mean(), group2[col].mean()], 
                          color=['#4c72b0', '#dd8452'], alpha=0.8)

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points", ha='center', va='bottom')

            ax.set_title(f'{col} 均值对比', fontproperties=prop, fontsize=14)
            ax.set_ylabel('均值', fontproperties=prop, fontsize=12)
            ax.set_xlabel('类别', fontproperties=prop, fontsize=12)
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
                f"数据集样本总数: {df.shape[0]}\n"
                f"特征列总数: {df.shape[1]}\n"
                f"目标变量 'target' 包含的类别数: {len(target_counts)}\n"
                f"类别1: {selected_targets[0]}, 样本数: {target_counts[selected_targets[0]]}\n"
                f"类别2: {selected_targets[1]}, 样本数: {target_counts[selected_targets[1]]}"
            ))
            pdf.ln(10)

            pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True, align='L')
            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True, align='L')
            pdf.ln(10)

            pdf.cell(200, 10, txt="图表可视化：", ln=True, align='L')
            for idx, img in enumerate(chart_images):
                pdf.cell(200, 10, txt=f"图表 {idx+1}: {top_diff_columns.index[idx]} 的均值对比", ln=True, align='L')
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



