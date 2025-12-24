import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="IT SLA & KPI Dashboard",
    layout="wide"
)

st.title("🖥️ IT SLA & KPI Dashboard")
st.caption("Monitoring Kinerja IT, SLA, dan Beban Kerja")

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

df = df.dropna(subset=["Tanggal Pengajuan"])

# ======================
# SLA CALCULATION
# ======================
today = pd.to_datetime(datetime.today().date())

df["Aging (Hari)"] = (today - df["Tanggal Pengajuan"]).dt.days

def sla_status(days):
    if days <= 1:
        return "🟢 On Time"
    elif days <= 3:
        return "🟡 Warning"
    else:
        return "🔴 Over SLA"

df["Status SLA"] = df["Aging (Hari)"].apply(sla_status)

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔎 Filter Data IT")

min_date = df["Tanggal Pengajuan"].min()
max_date = df["Tanggal Pengajuan"].max()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_bagian = st.sidebar.multiselect(
    "Bagian",
    sorted(df["Bagian"].unique()),
    default=sorted(df["Bagian"].unique())
)

selected_sla = st.sidebar.multiselect(
    "Status SLA",
    df["Status SLA"].unique(),
    default=df["Status SLA"].unique()
)

# ======================
# APPLY FILTER
# ======================
filtered_df = df[
    (df["Tanggal Pengajuan"] >= pd.to_datetime(date_range[0])) &
    (df["Tanggal Pengajuan"] <= pd.to_datetime(date_range[1])) &
    (df["Bagian"].isin(selected_bagian)) &
    (df["Status SLA"].isin(selected_sla))
]

# ======================
# KPI SECTION
# ======================
st.subheader("📌 IT Key Performance Indicators")

total = len(filtered_df)
on_time = len(filtered_df[filtered_df["Status SLA"] == "🟢 On Time"])
over_sla = len(filtered_df[filtered_df["Status SLA"] == "🔴 Over SLA"])
avg_aging = round(filtered_df["Aging (Hari)"].mean(), 2) if total else 0

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Tiket", total)
k2.metric("On Time (%)", f"{(on_time/total*100):.1f}%" if total else "0%")
k3.metric("Over SLA (%)", f"{(over_sla/total*100):.1f}%" if total else "0%")
k4.metric("Rata-rata Aging (Hari)", avg_aging)

# ======================
# SLA DISTRIBUTION
# ======================
st.subheader("🚦 Distribusi Status SLA")

sla_count = filtered_df["Status SLA"].value_counts()

fig1, ax1 = plt.subplots()
sla_count.plot(kind="bar", ax=ax1)
ax1.set_xlabel("Status SLA")
ax1.set_ylabel("Jumlah Tiket")
st.pyplot(fig1)

# ======================
# TREND BEBAN KERJA
# ======================
st.subheader("📈 Trend Beban Kerja IT")

trend = filtered_df.groupby("Tanggal Pengajuan").size()

fig2, ax2 = plt.subplots()
trend.plot(marker="o", ax=ax2)
ax2.set_xlabel("Tanggal")
ax2.set_ylabel("Jumlah Tiket")
ax2.grid(True)
st.pyplot(fig2)

# ======================
# ISSUE & BAGIAN
# ======================
c1, c2 = st.columns(2)

with c1:
    st.subheader("⚠️ Masalah Terbanyak")
    issue = filtered_df["Keterangan Masalah"].value_counts().head(10)
    fig3, ax3 = plt.subplots()
    issue.plot(kind="barh", ax=ax3)
    st.pyplot(fig3)

with c2:
    st.subheader("🏢 Bagian Over SLA")
    over_bagian = (
        filtered_df[filtered_df["Status SLA"] == "🔴 Over SLA"]
        ["Bagian"].value_counts()
    )
    fig4, ax4 = plt.subplots()
    over_bagian.plot(kind="barh", ax=ax4)
    st.pyplot(fig4)

# ======================
# DETAIL TABLE
# ======================
st.subheader("📋 Detail Tiket IT (Dengan SLA)")
st.dataframe(
    filtered_df.sort_values("Aging (Hari)", ascending=False),
    use_container_width=True
)
