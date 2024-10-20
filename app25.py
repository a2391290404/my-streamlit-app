# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os

# 设置页面标题
st.title("CSV 数据分析与可视化 - 自动差异分析")

# 上传CSV文件
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 假设第一列是 target 列
    target_col = df.columns[0]

    # 检查 target 列中的唯一值
    target_counts = df[target_col].value_counts()

    if len(target_counts) < 2:
        st.write("数据中的 target 列应至少包含两个不同的类。")
    else:
        # 自动选取 target 列中出现最多的两个类别
        selected_targets = target_counts.index[:2]
        st.write(f"自动选取的两个 target 类别为: {selected_targets[0]} 和 {selected_targets[1]}")

        # 分别获取这两个类别对应的子集数据
        group1 = df[df[target_col] == selected_targets[0]].drop(columns=[target_col])
        group2 = df[df[target_col] == selected_targets[1]].drop(columns=[target_col])

        # 计算每列的均值差异
        mean_diff = abs(group1.mean() - group2.mean())

        # 找到差异最大的列（前5名）
        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        # 可视化差异最大的几列
        st.write("差异最大的几列的比较：")
        for col in top_diff_columns.index:
            st.write(f"列: {col}")
            fig, ax = plt.subplots()
            ax.bar([f'{selected_targets[0]}', f'{selected_targets[1]}'], [group1[col].mean(), group2[col].mean()], color=['blue', 'red'])
            ax.set_title(f'{col} 差异比较')
            ax.set_ylabel('均值')
            for i, v in enumerate([group1[col].mean(), group2[col].mean()]):
                ax.text(i, v + 0.2, f"{v:.2f}", ha='center')
            st.pyplot(fig)

        # 生成 PDF 报告
        if st.button('生成 PDF 报告'):
            pdf = FPDF()
            pdf.add_page()

            # 确保字体文件路径正确
            font_path = os.path.join(os.getcwd(), "SimHei.ttf")
            pdf.add_font("SimHei", "", font_path, uni=True)

            # 设置字体
            pdf.set_font("SimHei", size=12)

            # PDF 报告标题
            pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
            pdf.cell(200, 10, txt="按 target 分组的差异分析", ln=True, align='C')

            # 写入差异分析结果
            pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True)
            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True)

            # 保存图表为图片并插入到 PDF
            for col in top_diff_columns.index:
                fig, ax = plt.subplots()
                ax.bar([f'{selected_targets[0]}', f'{selected_targets[1]}'], [group1[col].mean(), group2[col].mean()], color=['blue', 'red'])
                ax.set_title(f'{col} 差异比较')
                ax.set_ylabel('均值')
                for i, v in enumerate([group1[col].mean(), group2[col].mean()]):
                    ax.text(i, v + 0.2, f"{v:.2f}", ha='center')

                # 保存图像
                img_path = f'{col}_comparison.png'
                fig.savefig(img_path)
                plt.close(fig)

                # 将图像插入 PDF
                pdf.image(img_path, x=10, y=None, w=100)

            # 将 PDF 保存到字节流中
            pdf_output = io.BytesIO()
            pdf_name = "data_analysis_report.pdf"
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # 下载生成的 PDF 文件
            st.download_button(
                label="下载 PDF 报告",
                data=pdf_output,
                file_name=pdf_name,
                mime="application/pdf"
            )

else:
    st.write("请上传 CSV 文件。")



