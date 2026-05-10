import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="EWS Bloat Sheep 3D", layout="wide")

st.title("🐑 Sistem Pemantauan Otomatis CCTV 3D - Deteksi Bloat")
st.markdown("""
Aplikasi ini mensimulasikan pemantauan volume rumen domba secara real-time menggunakan sensor 3D.
""")

# --- FUNGSI SIMULASI DATA 3D ---
def generate_rumen_point_cloud(bloat_factor=1.0):
    """Mensimulasikan point cloud area abdomen kiri domba."""
    n_points = 1000
    phi = np.random.uniform(0, np.pi, n_points)
    theta = np.random.uniform(0, np.pi, n_points)
    
    # Membuat bentuk ellipsoid (simulasi perut)
    x = 1.5 * np.sin(phi) * np.cos(theta)
    y = (1.0 * bloat_factor) * np.sin(phi) * np.sin(theta) # Sumbu Y adalah tingkat kembung
    z = 2.0 * np.cos(phi)
    
    # Filter hanya untuk area fosa paralumbar (abdomen kiri)
    mask = y > 0
    return x[mask], y[mask], z[mask]

# --- SIDEBAR: KONTROL SISTEM ---
st.sidebar.header("⚙️ Konfigurasi Sensor & CCTV")
sheep_id = st.sidebar.selectbox("Pilih ID Domba", ["DMB-001", "DMB-002", "DMB-003"])
threshold_warning = st.sidebar.slider("Ambang Batas Warning (%)", 10, 20, 15)
threshold_critical = st.sidebar.slider("Ambang Batas Critical (%)", 21, 40, 25)

# Simulasi Baseline Volume (Litre)
baseline_vol = 15.0 

# --- LOGIKA MONITORING ---
st.sidebar.subheader("🕹️ Simulasi Kondisi")
condition = st.sidebar.select_slider(
    "Status Domba saat ini:",
    options=["Normal", "Mulai Kembung", "Kembung Akut"]
)

if condition == "Normal":
    current_factor = np.random.uniform(1.0, 1.05)
elif condition == "Mulai Kembung":
    current_factor = np.random.uniform(1.12, 1.18)
else:
    current_factor = np.random.uniform(1.25, 1.40)

current_vol = baseline_vol * current_factor
increase_pct = (current_vol - baseline_vol) / baseline_vol * 100

# --- DASHBOARD UTAMA ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Volume Rumen Saat Ini", f"{current_vol:.2f} L", f"{increase_pct:.1f}%")

with col2:
    status_color = "green"
    if increase_pct >= threshold_critical:
        status_label = "CRITICAL"
        status_color = "red"
    elif increase_pct >= threshold_warning:
        status_label = "WARNING"
        status_color = "orange"
    else:
        status_label = "SAFE"
    
    st.markdown(f"### Status: <span style='color:{status_color}'>{status_label}</span>", unsafe_allow_html=True)

with col3:
    st.metric("Sensor Latency", "45ms", "Optimal")

st.divider()

# --- VISUALISASI 3D ---
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Visualisasi Point Cloud 3D (Area Rumen)")
    x, y, z = generate_rumen_point_cloud(current_factor)
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=3,
            color=y,                # Warna berdasarkan distensi
            colorscale='Viridis',   # Skala warna
            opacity=0.8
        )
    )])
    
    fig.update_layout(
        scene=dict(
            xaxis_title='Panjang (x)',
            yaxis_title='Distensi (y)',
            zaxis_title='Tinggi (z)',
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Log EWS")
    log_data = {
        "Waktu": ["10:00", "10:05", "10:10", "10:15"],
        "Vol (L)": [15.1, 15.2, 17.5, current_vol],
        "Status": ["Normal", "Normal", "Warning", status_label]
    }
    st.table(pd.DataFrame(log_data))
    
    if status_label == "CRITICAL":
        st.error("🚨 PERINGATAN: Deteksi Distensi Gas Berlebih! Segera periksa Domba ID " + sheep_id)
        st.button("Kirim Notifikasi ke Petugas")

# --- CHART HISTORIS ---
st.subheader("Tren Perubahan Volume (24 Jam Terakhir)")
chart_data = pd.DataFrame(
    np.random.randn(20, 1) * 0.5 + current_vol,
    columns=['Volume (L)']
)
st.line_chart(chart_data)

st.info("**Catatan Teknis:** Data 3D di atas adalah simulasi rekonstruksi fosa paralumbar kiri. Dalam sistem nyata, noise dari bulu akan difilter menggunakan algoritma Gaussian Smoothing.")