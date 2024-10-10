# %%
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("CSV 文件数据分析与可视化")

uploaded_file = st.file_uploader("上传一个 CSV 文件", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("数据预览")
    st.write(df.head())

    columns = st.multiselect("选择一个或多个列进行比较", df.select_dtypes(include=[np.number]).columns)

    if columns:
        st.subheader(f"选择的列: {', '.join(columns)}")

        st.write("描述性统计:")
        st.write(df[columns].describe())

        st.subheader("选择列的折线图")
        fig, ax = plt.subplots()
        for col in columns:
            ax.plot(df[col], label=col)
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.set_title("选择列的折线图")
        ax.legend()
        st.pyplot(fig)

        st.subheader("选择列的箱线图")
        fig, ax = plt.subplots()
        ax.boxplot([df[col].dropna() for col in columns], labels=columns)
        ax.set_title("选择列的箱线图")
        st.pyplot(fig)
    else:
        st.write("请选择至少一个列进行比较。")
else:
    st.write("请上传 CSV 文件。")



