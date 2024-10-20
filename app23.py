# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

st.title("CSV 数据分析与可视化 - 自动差异分析")
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:
    # 读取 CSV 文件
    df = pd.read_csv(uploaded_file)

    target_col = df.columns[0]
    
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
        top_diff_columns = mean_diff.sort_values(ascending=False).head(5)

        st.write("差异最大的列及其差异值：")
        st.write(top_diff_columns)

        st.write("差异最大的几列的比较：")
        for col in top_diff_columns.index:
            st.write(f"列: {col}")
            fig, ax = plt.subplots()
            ax.bar([selected_targets[0], selected_targets[1]], [group1[col].mean(), group2[col].mean()], color=['blue', 'red'])
            ax.set_title(f"{col} 差异对比图")
            ax.set_ylabel("均值")
            for i, v in enumerate([group1[col].mean(), group2[col].mean()]):
                ax.text(i, v, f"{v:.2f}", ha='center', va='bottom')
            st.pyplot(fig)

        # 生成相关性矩阵
        combined_data = pd.concat([group1[top_diff_columns.index], group2[top_diff_columns.index]])
        corr_matrix = combined_data.corr()
        st.write("差异最大的几列的相关性矩阵：")
        st.write(corr_matrix)

        # 生成PDF报告
        if st.button('生成 PDF 报告'):
            pdf = FPDF()
            pdf.add_page()

            # 添加中文字体（使用 SimHei 字体）
            pdf.add_font("SimHei", "", "SimHei.ttf", uni=True)
            pdf.set_font("SimHei", size=12)

            # 标题
            pdf.cell(200, 10, txt="CSV 数据分析报告", ln=True, align='C')
            pdf.cell(200, 10, txt="按 target 分组的差异分析", ln=True, align='C')

            # 目标描述
            pdf.cell(200, 10, txt="目标：预测用户是否购买产品", ln=True)
            pdf.multi_cell(0, 10, txt="本分析的目的是基于用户数据预测其是否会购买产品。如果购买可能性大，我们将定向投放广告，从而优化广告成本。通过采集用户行为数据并量化特征，我们可以找到影响用户购买决策的关键因素。")

            # 数据描述
            pdf.cell(200, 10, txt="数据描述：", ln=True)
            pdf.multi_cell(0, 10, txt=f"此数据集包含 {df.shape[0]} 行和 {df.shape[1]} 列，其中第一列是目标列（target），其余列是用户行为特征。")

            # 差异最大的特征分析
            pdf.cell(200, 10, txt="差异最大的列及其差异值：", ln=True)
            for col, diff in top_diff_columns.items():
                pdf.cell(200, 10, txt=f"{col}: {diff:.4f}", ln=True)

            # 相关性矩阵
            pdf.cell(200, 10, txt="相关性矩阵：", ln=True)
            for row in corr_matrix.index:
                row_data = ', '.join([f"{val:.2f}" for val in corr_matrix.loc[row]])
                pdf.cell(200, 10, txt=f"{row}: {row_data}", ln=True)

            # 图表解释
            pdf.cell(200, 10, txt="图表说明：", ln=True)
            for col in top_diff_columns.index:
                pdf.cell(200, 10, txt=f"图表 {col}: 展示了 {selected_targets[0]} 和 {selected_targets[1]} 在此特征上的差异。", ln=True)

            # 生成总结
            pdf.cell(200, 10, txt="总结：", ln=True)
            pdf.multi_cell(0, 10, txt="通过分析，发现特征 var_74 和 var_102 对用户购买行为有显著影响。建议进一步研究这些特征，并在广告投放策略中优先考虑这些影响较大的特征。定向投放广告可以有效减少不必要的广告支出，提升广告投放效果。")

            # 保存PDF到内存
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # 下载生成的PDF文件
            st.download_button(
                label="下载 PDF 报告",
                data=pdf_output,
                file_name="data_analysis_report.pdf",
                mime="application/pdf"
            )



