import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os

# Streamlit 界面
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

        # 计算每列的均值差异
        mean_diff = abs(group1.mean() - group2.mean())
        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)
        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        # 绘制图像并保存为文件
        image_paths = []
        for col in top_diff_columns.index:
            fig, ax = plt.subplots()
            ax.bar([f'{selected_targets[0]}', f'{selected_targets[1]}'],
                   [group1[col].mean(), group2[col].mean()],
                   color=['blue', 'red'])
            ax.set_title(f'{col} 比较图')
            ax.set_xlabel("类别")
            ax.set_ylabel("均值")
            # 保存图像
            image_path = f"{col}_comparison.png"
            fig.savefig(image_path)
            image_paths.append(image_path)
            plt.close(fig)

        st.write("图表已生成，开始创建 PDF 报告...")

        # PDF 生成
        pdf = FPDF()
        pdf.add_page()

        # 添加中文字体（确保字体文件 SimHei.ttf 在项目目录中）
        pdf.add_font("SimHei", "", "SimHei.ttf", uni=True)
        pdf.set_font("SimHei", size=12)

        # 添加标题
        pdf.set_font("SimHei", "B", 16)
        pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
        pdf.set_font("SimHei", size=12)
        pdf.cell(200, 10, txt="按 target 分组的差异分析", ln=True, align='C')

        # 添加说明性文本
        pdf.ln(10)
        pdf.cell(200, 10, txt="目标：预测用户是否购买产品", ln=True)
        pdf.multi_cell(0, 10, "本分析的目的是基于用户数据预测其是否会购买产品。如果购买可能性大，我们将定向投放广告，从而优化广告成本。通过采集用户行为数据并量化特征，我们可以找到影响用户购买决策的关键因素。")

        # 添加差异最大列表格
        pdf.ln(10)
        pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True)
        pdf.set_font("SimHei", size=10)
        for col, diff in top_diff_columns.items():
            pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True)

        # 添加图像
        pdf.ln(10)
        for image_path in image_paths:
            pdf.image(image_path, x=10, w=100)
            pdf.ln(10)

        # 保存 PDF 到内存
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        # 下载 PDF
        st.download_button(
            label="下载 PDF 报告",
            data=pdf_output,
            file_name="data_analysis_report.pdf",
            mime="application/pdf"
        )

        # 清理生成的图像文件
        for image_path in image_paths:
            os.remove(image_path)

