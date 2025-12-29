import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# ======================
# PDF GENERATOR
# ======================
def generate_pdf(filtered_df, start_date, end_date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>LAPORAN KINERJA IT</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"Periode Laporan: {start_date} s/d {end_date}",
            styles["Normal"]
        )
    )
    elements.append(Spacer(1, 12))

    total = len(filtered_df)

    elements.append(Paragraph("<b>Ringkasan KPI</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Total Tiket IT: {total}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    if not filtered_df.empty:
        top_issue = filtered_df["Keterangan Masalah"].value_counts().idxmax()
        elements.append(Paragraph(f"Masalah Terbanyak: {top_issue}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>10 Tiket Terbaru</b>", styles["Heading2"]))

        latest_df = (
            filtered_df
            .sort_values("Tanggal Pengajuan", ascending=False)
            .head(10)
        )

        table_data = [["Tanggal", "Bagian", "User", "Masalah"]]

        for _, row in latest_df.iterrows():
            table_data.append([
                row["Tanggal Pengajuan"].strftime("%d-%m-%Y"),
                row["Bagian"],
                row["User"],
                row["Keterangan Masalah"]
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))

        elements.append(table)
    else:
        elements.append(Paragraph("Tidak ada data pada periode ini.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ======================
# CONFIG
# ======================
st.set_page_config(page_title="IT Performance Dashboard", layout="wide")
st.title("🖥️ IT Performance Dashboard")
st.caption("Monitoring Beban Kerja & Masalah IT")

# ======================
# UPLOAD FILE
# ======================
uploaded_file = st.file_uploader("📂 Upload File CSV Data IT", type=["csv"])

if not uploaded_file:
    st.info("Silakan upload file CSV untuk mulai analisis IT")
    st.stop()

df = pd.read_csv(uploaded_file)

# ======================
# DATE CLEANING
# ======================
df["Tanggal Pengajuan"] = pd.to_datetime(
    df["Tanggal Pengajuan"].astype(str).str.strip(),
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔎 Filter Data IT")

min_date = df["Tanggal Pengajuan"].min()
max_date = df["Tanggal Pengajuan"].max()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date)
)

# Handle kalau user pilih 1 tanggal
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

bagian_list = sorted(df["Bagian"].dropna().unique())
selected_bagian = st.sidebar.multiselect(
    "Bagian",
    bagian_list,
    default=bagian_list
)

filtered_df = df[
    (df["Tanggal Pengajuan"] >= pd.to_datetime(start_date)) &
    (df["Tanggal Pengajuan"] <= pd.to_datetime(end_date)) &
    (df["Bagian"].isin(selected_bagian))
]

# ======================
# KPI
# ======================
st.subheader("📌 IT Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Tiket IT", len(filtered_df))
k2.metric("Total User Dilayani", filtered_df["User"].nunique())
k3.metric("Total Bagian", filtered_df["Bagian"].nunique())

top_issue = (
    filtered_df["Keterangan Masalah"].value_counts().idxmax()
    if not filtered_df.empty else "-"
)
k4.metric("Masalah Terbanyak", top_issue)

# ======================
# TREND
# ======================
st.subheader("📈 Trend Beban Kerja IT")

trend = filtered_df.groupby("Tanggal Pengajuan").size()

if not trend.empty:
    fig1, ax1 = plt.subplots()
    trend.plot(marker="o", ax=ax1)
    ax1.set_xlabel("Tanggal")
    ax1.set_ylabel("Jumlah Tiket")
    ax1.grid(True)
    st.pyplot(fig1)
else:
    st.info("Tidak ada data trend.")

# ======================
# ISSUE ANALYSIS
# ======================
st.subheader("⚠️ Analisis Masalah IT")

c1, c2 = st.columns(2)

with c1:
    issue_count = filtered_df["Keterangan Masalah"].value_counts().head(10)
    if not issue_count.empty:
        fig2, ax2 = plt.subplots()
        issue_count.plot(kind="barh", ax=ax2)
        st.pyplot(fig2)

with c2:
    bagian_count = filtered_df["Bagian"].value_counts()
    if not bagian_count.empty:
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
st.pyplot(fig4)

# ======================
# ADMIN ANALYSIS
# ======================
if "Admin" in filtered_df.columns:
    st.subheader("👨‍💼 Analisis Admin")
    admin_count = filtered_df["Admin"].value_counts().head(10)
    fig5, ax5 = plt.subplots()
    admin_count.plot(kind="bar", ax=ax5)
    st.pyplot(fig5)

# ======================
# EXPORT PDF
# ======================
st.subheader("📥 Export Laporan")

pdf_buffer = generate_pdf(filtered_df, start_date, end_date)

st.download_button(
    "📄 Download Laporan PDF",
    data=pdf_buffer,
    file_name="Laporan_Kinerja_IT.pdf",
    mime="application/pdf"
)

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Detail Data Tiket IT")
st.dataframe(filtered_df, use_container_width=True)
