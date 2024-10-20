# %%
import streamlit as st
import pandas as pd
import numpy as np

st.title("CSV 数据分析与可视化 - 按 target 分组")
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    target_col = df.columns[0]

    target_groups = df.groupby(target_col)
    unique_targets = df[target_col].unique()
    
    if len(unique_targets) != 2:
        st.write("数据中的 target 列应仅包含两类。")
    else:

        group1 = target_groups.get_group(unique_targets[0]).drop(columns=[target_col])
        group2 = target_groups.get_group(unique_targets[1]).drop(columns=[target_col])

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



