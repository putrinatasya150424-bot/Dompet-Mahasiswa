import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dompet Mahasiswa", page_icon="🎓💸", layout="wide")
st.title("🎓💸 Dompet Mahasiswa — All-in-One Finance App")

# Initialize Data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Tanggal", "Tipe", "Deskripsi", "Jumlah"])

df = st.session_state.data

# --------- INPUT DATA ---------
st.sidebar.header("➕ Tambah Transaksi")
tanggal = st.sidebar.date_input("Tanggal", datetime.now())
tipe = st.sidebar.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
deskripsi = st.sidebar.text_input("Deskripsi")
jumlah = st.sidebar.number_input("Jumlah (Rp)", min_value=0)

if st.sidebar.button("Tambah"):
    if deskripsi and jumlah > 0:
        new_row = {"Tanggal": tanggal, "Tipe": tipe, "Deskripsi": deskripsi, "Jumlah": jumlah}
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Transaksi berhasil ditambahkan! 🎉")
    else:
        st.warning("Isi deskripsi dan jumlah!")

st.sidebar.markdown("---")

# --------- PROSES DATA ---------
if df.empty:
    st.info("Belum ada transaksi. Tambahkan data di sebelah kiri ya!")
    st.stop()

df["Tanggal"] = pd.to_datetime(df["Tanggal"])
df["Bulan"] = df["Tanggal"].dt.to_period("M").astype(str)
df["Minggu"] = df["Tanggal"].dt.isocalendar().week.astype(str)

# Pilih Mode Tampilan
mode = st.radio("Pilih Mode Tampilan", ["Bulanan", "Mingguan"])
periode_col = "Bulan" if mode == "Bulanan" else "Minggu"

# Agregasi
grouped = df.groupby([periode_col, "Tipe"])["Jumlah"].sum().unstack(fill_value=0)
grouped["Net"] = grouped["Pemasukan"] - grouped["Pengeluaran"]

total_income = df[df["Tipe"]=="Pemasukan"]["Jumlah"].sum()
total_expense = df[df["Tipe"]=="Pengeluaran"]["Jumlah"].sum()
net = total_income - total_expense

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {total_income:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {total_expense:,.0f}")
col3.metric("Saldo / Sisa Uang", f"Rp {net:,.0f}",
            delta=f"{net:,.0f}", delta_color="normal")

# Line Chart
st.subheader(f"📈 Tren {mode} Keuangan")
fig_line = px.line(grouped.reset_index(), x=periode_col,
                   y=["Pemasukan", "Pengeluaran", "Net"], markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# Pie Chart Pengeluaran
st.subheader(f"🥧 Komposisi Pengeluaran per {mode}")
selected_periode = st.selectbox(f"Pilih {mode}", grouped.index)
df_sel = df[df[periode_col] == selected_periode]
exp_sel = df_sel[df_sel["Tipe"]=="Pengeluaran"]

if not exp_sel.empty:
    fig_pie = px.pie(exp_sel, names="Deskripsi", values="Jumlah",
                     title=f"Pengeluaran {selected_periode}")
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("Belum ada pengeluaran pada periode ini.")

# Tabel
st.subheader("📋 Detail Transaksi")
st.dataframe(df)

# Export CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Data (.csv)",
                   data=csv,
                   file_name="dompet_mahasiswa.csv",
                   mime="text/csv")

st.success("Data tersimpan selama aplikasi dibuka ✨")
