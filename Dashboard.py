import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="IT Performance Dashboard",
    layout="wide"
)

st.title("🖥️ IT Performance Dashboard")
st.caption("Monitoring Beban Kerja & Masalah IT")

# ======================
# UPLOAD FILE
# ======================
uploaded_file = st.file_uploader(
    "📂 Upload File CSV Data IT",
    type=["csv"]
)

if not uploaded_file:
    st.info("Silakan upload file CSV untuk mulai analisis IT")
    st.stop()

# ======================
# LOAD DATA
# ======================
df = pd.read_csv(uploaded_file)

# ======================
# DATE CLEANING
# ======================
df["Tanggal Pengajuan"] = (
    df["Tanggal Pengajuan"]
    .astype(str)
    .str.strip()
)

df["Tanggal Pengajuan"] = pd.to_datetime(
    df["Tanggal Pengajuan"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔎 Filter Data IT")

# Filter tanggal
min_date = df["Tanggal Pengajuan"].min()
max_date = df["Tanggal Pengajuan"].max()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter bagian
bagian_list = sorted(df["Bagian"].dropna().unique())
selected_bagian = st.sidebar.multiselect(
    "Bagian",
    bagian_list,
    default=bagian_list
)

# ======================
# APPLY FILTER
# ======================
filtered_df = df[
    (df["Tanggal Pengajuan"] >= pd.to_datetime(date_range[0])) &
    (df["Tanggal Pengajuan"] <= pd.to_datetime(date_range[1])) &
    (df["Bagian"].isin(selected_bagian))
]

# ======================
# KPI SECTION
# ======================
st.subheader("📌 IT Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Tiket IT", len(filtered_df))
k2.metric("Total User Dilayani", filtered_df["User"].nunique())
k3.metric("Total Bagian", filtered_df["Bagian"].nunique())

top_issue = (
    filtered_df["Keterangan Masalah"]
    .value_counts()
    .idxmax()
    if not filtered_df.empty else "-"
)
k4.metric("Masalah Terbanyak", top_issue)

# ======================
# TREND TIKET
# ======================
st.subheader("📈 Trend Beban Kerja IT")

trend = (
    filtered_df
    .dropna(subset=["Tanggal Pengajuan"])
    .groupby("Tanggal Pengajuan")
    .size()
)

fig1, ax1 = plt.subplots()
trend.plot(marker="o", ax=ax1)
ax1.set_xlabel("Tanggal")
ax1.set_ylabel("Jumlah Tiket")
ax1.grid(True)
st.pyplot(fig1)

# ======================
# ISSUE ANALYSIS
# ======================
st.subheader("⚠️ Analisis Masalah IT")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Jenis Masalah Terbanyak**")
    issue_count = filtered_df["Keterangan Masalah"].value_counts().head(10)
    fig2, ax2 = plt.subplots()
    issue_count.plot(kind="barh", ax=ax2)
    st.pyplot(fig2)

with c2:
    st.markdown("**Bagian Paling Sering Bermasalah**")
    bagian_count = filtered_df["Bagian"].value_counts()
    fig3, ax3 = plt.subplots()
    bagian_count.plot(kind="barh", ax=ax3)
    st.pyplot(fig3)

# ======================
# USER ANALYSIS
# ======================
st.subheader("👤 Analisis User")

user_count = filtered_df["User"].value_counts().head(10)

fig4, ax4 = plt.subplots()
user_count.plot(kind="bar", ax=ax4)
ax4.set_xlabel("User")
ax4.set_ylabel("Jumlah Tiket")
st.pyplot(fig4)

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Detail Data Tiket IT")
st.dataframe(filtered_df, use_container_width=True)
