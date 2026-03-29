import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Bike Sharing Dashboard", 
    page_icon="https://play-lh.googleusercontent.com/P_PSOKvARCq6SUcl1oddA2W5a4xYRGwkf8r8fuBvZW_s5IUQ_qEprYBjeYo9fyGBCQ", 
    layout="wide"
    )

# LOAD & CLEAN DATA
@st.cache_data
def load_data():
    day_df = pd.read_csv('day_cleaned.csv')
    hour_df = pd.read_csv('hour_cleaned.csv')
    
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    return day_df, hour_df

day_df, hour_df = load_data()

# SIDEBAR NAVIGASI
st.sidebar.image("https://play-lh.googleusercontent.com/P_PSOKvARCq6SUcl1oddA2W5a4xYRGwkf8r8fuBvZW_s5IUQ_qEprYBjeYo9fyGBCQ", 
                width = 100
                )
st.sidebar.title("Dashboard")

if 'halaman' not in st.session_state:
    st.session_state['halaman'] = "Overview"


if st.sidebar.button("Overview", use_container_width=True):
    st.session_state['halaman'] = "Overview"

if st.sidebar.button("RFM Analysis", use_container_width=True):
    st.session_state['halaman'] = "RFM Analysis"

if st.sidebar.button("Clustering Analysis", use_container_width=True):
    st.session_state['halaman'] = "Clustering Analysis"

menu = st.session_state['halaman']

# HALAMAN OVERVIEW
if menu == "Overview":
    st.title("Bike Sharing Data Dashboard")
    st.markdown("Selamat datang di dashboard analisis penyewaan sepeda.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Penyewaan (2 Tahun)", f"{day_df['cnt'].sum():,.0f}")
    with col2:
        st.metric("Total Pelanggan Registered", f"{day_df['registered'].sum():,.0f}")
    with col3:
        st.metric("Total Pelanggan Casual", f"{day_df['casual'].sum():,.0f}")
        
    st.subheader("Tren Penyewaan Harian")
    fig, ax = plt.subplots(figsize=(16, 5))
    sns.lineplot(x='dteday', y='cnt', data=day_df, ax=ax, color='#1f77b4')
    ax.set_title("Total Penyewaan Sepeda (2011 - 2012)")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Total Sewa")
    st.pyplot(fig)
    
    st.info("""
    **Insight Overview:**
    - **Tren Positif & Musiman:** Terlihat pertumbuhan penyewaan yang signifikan dari tahun 2011 ke 2012. Permintaan sangat dipengaruhi oleh musim, di mana penyewaan memuncak di Musim Panas/Gugur dan anjlok di Musim Dingin.
    - **Karakteristik Penggunaan:** Layanan ini didominasi oleh aktivitas komuter di hari kerja (*weekday*), namun tetap memiliki segmen rekreasi yang kuat di akhir pekan (*weekend*).
    """)

# HALAMAN RFM ANALYSIS
elif menu == "RFM Analysis":
    st.title("RFM Analysis (Casual vs Registered)")
    st.markdown("Analisis ini membandingkan metrik Recency, Frequency, dan Monetary antara pengguna Casual dan Registered.")
    
    last_date = day_df['dteday'].max()
    rfm_data = {
        'User_Type': ['Casual', 'Registered'],
        'Recency_Days_Ago': [(last_date - day_df[day_df['casual'] > 0]['dteday'].max()).days, 
                             (last_date - day_df[day_df['registered'] > 0]['dteday'].max()).days],
        'Frequency_Avg_Daily': [day_df['casual'].mean(), day_df['registered'].mean()],
        'Monetary_Total_Volume': [day_df['casual'].sum(), day_df['registered'].sum()]
    }
    rfm_df = pd.DataFrame(rfm_data)
    st.dataframe(rfm_df)
    
    st.subheader("Visualisasi Metrik RFM")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    colors = ['#d3d3d3', '#1f77b4']
    
    sns.barplot(x='User_Type', y='Recency_Days_Ago', data=rfm_df, ax=axes[0], palette=colors)
    axes[0].set_title('Recency (Hari Sejak Sewa Terakhir)')
    axes[0].set_ylim(0, 1)
    
    sns.barplot(x='User_Type', y='Frequency_Avg_Daily', data=rfm_df, ax=axes[1], palette=colors)
    axes[1].set_title('Frequency (Rata-rata Sewa Harian)')
    
    sns.barplot(x='User_Type', y='Monetary_Total_Volume', data=rfm_df, ax=axes[2], palette=colors)
    axes[2].set_title('Monetary (Total Volume Sewa)')
    
    st.pyplot(fig)

    st.info("""
    **Insight:**
    * **Pelanggan Registered adalah "Backbone":** Mereka memiliki tingkat *Frequency* dan *Monetary* yang jauh lebih masif, menjadikannya tulang punggung bisnis dengan pendapatan yang stabil.
    * **Strategi Bisnis:** Perusahaan harus menyeimbangkan antara mempertahankan retensi pelanggan *Registered* (memastikan ketersediaan armada untuk mereka) dan melakukan kampanye konversi agresif (promo/membership) untuk mengubah pengguna *Casual* menjadi pelanggan tetap.
    """)
    
# HALAMAN 3: CLUSTERING ANALYSIS
elif menu == "Clustering Analysis":
    st.title("Clustering Analysis")
    
    # 1. Binning
    day_df['Demand_Level'] = pd.qcut(day_df['cnt'], q=3, labels=['Low Demand', 'Medium Demand', 'High Demand'])
    demand_counts = day_df['Demand_Level'].value_counts().reindex(['Low Demand', 'Medium Demand', 'High Demand']).reset_index()
    demand_counts.columns = ['Demand_Level', 'Jumlah_Hari']
    
    # 2. Manual Grouping
    def categorize_time(hr):
        if 6 <= hr <= 9: return 'Morning Rush (06-09)'
        elif 10 <= hr <= 15: return 'Mid-Day (10-15)'
        elif 16 <= hr <= 19: return 'Evening Rush (16-19)'
        else: return 'Night/Early (20-05)'
        
    hour_df['Time_Group'] = hour_df['hr'].apply(categorize_time)
    time_group_avg = hour_df.groupby('Time_Group')['cnt'].mean().reindex([
        'Morning Rush (06-09)', 'Mid-Day (10-15)', 'Evening Rush (16-19)', 'Night/Early (20-05)'
    ]).reset_index()
    time_group_avg.columns = ['Kategori_Waktu', 'Rata_rata_Sewa']
    
    st.subheader("Tabel Hasil Clustering")
    
    # Membagi layout menjadi 2 kolom untuk tabel
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Hasil Binning (Tingkat Permintaan)**")
        st.dataframe(demand_counts)
    with col2:
        st.markdown("**2. Hasil Manual Grouping (Jam Operasional)**")
        st.dataframe(time_group_avg)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    max_demand = demand_counts['Jumlah_Hari'].max()
    colors_demand = ['#1f77b4' if val == max_demand else '#d3d3d3' for val in demand_counts['Jumlah_Hari']]
    sns.barplot(x='Demand_Level', y='Jumlah_Hari', data=demand_counts, ax=axes[0], palette=colors_demand)
    axes[0].set_title('Binning: Distribusi Hari Berdasarkan Permintaan')
    
    max_time = time_group_avg['Rata_rata_Sewa'].max()
    colors_time = ['#1f77b4' if val == max_time else '#d3d3d3' for val in time_group_avg['Rata_rata_Sewa']]
    sns.barplot(x='Kategori_Waktu', y='Rata_rata_Sewa', data=time_group_avg, ax=axes[1], palette=colors_time)
    axes[1].set_title('Manual Grouping: Rata-rata Sewa per Kategori Waktu')
    plt.xticks(rotation=15)
    
    st.pyplot(fig)
    
    st.info("""
    **Insight:**
    - Hari dengan tingkat permintaan *Low, Medium,* dan *High* terbagi rata, masing-masing 244 hari (Pada high demand hanya berbeda 1 hari saja, yaitu 243 hari). Ini menunjukkan bisnis berjalan stabil tanpa ketimpangan ekstrem antara hari sepi dan hari sibuk.
    - Jam *Evening Rush* (16:00 - 19:59) mencatat penyewaan tertinggi (±378 unit/jam). Mobilitas pulang kerja atau aktivitas sore adalah momen krusial yang menuntut ketersediaan sepeda maksimal.
    - Penyewaan di siang hari / *Mid-Day* (± 230 unit/jam) ternyata mengalahkan jam komuter pagi (± 216 unit/jam). Aktivitas seperti makan siang, perjalanan dekat, atau rekreasi turis menyumbang *traffic* yang sangat signifikan.
    """)
