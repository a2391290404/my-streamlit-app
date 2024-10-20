# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# 设定标题
st.title("CSV 数据分析与可视化 - 自动差异分析")
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:
    # 读取 CSV 文件
    df = pd.read_csv(uploaded_file)

    # 假设第一列是 target 列
    target_col = df.columns[0]
    
    # 获取 target 列中类别的数量
    target_counts = df[target_col].value_counts()

    # 检查是否有至少两个类别
    if len(target_counts) < 2:
        st.write("数据中的 target 列应至少包含两个不同的类。")
    else:
        # 自动选取出现最多的两个类别
        selected_targets = target_counts.index[:2]
        st.write(f"自动选取的两个 target 类别为: {selected_targets[0]} 和 {selected_targets[1]}")

        # 分别获取两个类别的子集数据
        group1 = df[df[target_col] == selected_targets[0]].drop(columns=[target_col])
        group2 = df[df[target_col] == selected_targets[1]].drop(columns=[target_col])

        # 计算每列的均值差异
        mean_diff = abs(group1.mean() - group2.mean())
        # 取前5个差异最大的列
        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        # 可视化差异最大的几列
        st.write("差异最大的几列的比较（柱状图）：")
        chart_images = []
        for col in top_diff_columns.index:
            st.write(f"列: {col}")

            # 使用柱状图确保即便数据量较少也能显示
            fig, ax = plt.subplots()
            ax.bar([f'{selected_targets[0]}', f'{selected_targets[1]}'],
                   [group1[col].mean(), group2[col].mean()], color=['blue', 'red'])
            ax.set_title(f'{col} 的均值对比')
            st.pyplot(fig)
            
            # 保存图表为图片
            img = io.BytesIO()
            fig.savefig(img, format='png')
            img.seek(0)
            chart_images.append(img)

        # 生成 PDF 报告
        if st.button('生成 PDF 报告'):
            pdf = FPDF()
            pdf.add_page()

            # 添加字体以支持中文
            pdf.add_font("SimHei", "", "SimHei.ttf", uni=True)
            pdf.set_font("SimHei", size=12)

            # 添加标题和描述
            pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
            pdf.multi_cell(0, 10, txt="目标：通过分析用户数据，预测用户是否会购买产品。此报告展示了根据不同特征的差异，分析目标客户的购买可能性。")

            # 差异最大的列及其差异值
            pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True)
            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True)

            # 添加图表到 PDF
            pdf.cell(200, 10, txt="图表可视化：", ln=True)
            for idx, img in enumerate(chart_images):
                pdf.cell(200, 10, txt=f"图表 {idx+1}: {top_diff_columns.index[idx]} 的均值对比", ln=True)
                pdf.image(img, x=10, y=None, w=190)

            # 保存 PDF 并提供下载
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # PDF 下载按钮
            st.download_button(
                label="下载 PDF 报告",
                data=pdf_output,
                file_name="data_analysis_report.pdf",
                mime="application/pdf"
            )



