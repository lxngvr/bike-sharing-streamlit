import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# SIDEBAR
st.sidebar.image("https://play-lh.googleusercontent.com/P_PSOKvARCq6SUcl1oddA2W5a4xYRGwkf8r8fuBvZW_s5IUQ_qEprYBjeYo9fyGBCQ",
                width = 100
                )
st.sidebar.title("Dashboard")
st.sidebar.markdown("---")
# Mapping opsi Musim (1: Spring, 2: Summer, 3: Fall, 4: Winter)
season_mapping = {
    1: "Musim Semi",
    2: "Musim Panas",
    3: "Musim Gugur",
    4: "Musim Dingin"
}

# FITUR INTERAKTIF (Dropdown untuk memilih Musim)
pilihan_musim = st.sidebar.selectbox(
    label='Pilih Musim',
    options=['Semua Musim', 'Musim Panas', 'Musim Gugur', 'Musim Dingin', 'Musim Semi']
)

# Filtering Dataframe Musim
if pilihan_musim == 'Semua Musim':
    main_day_df = day_df
    main_hour_df = hour_df
else:
    season_code = [k for k, v in season_mapping.items() if v == pilihan_musim][0]
    main_day_df = day_df[day_df['season'] == season_code]
    main_hour_df = hour_df[hour_df['season'] == season_code]

st.sidebar.markdown("---")

# Navigasi Halaman
if 'halaman' not in st.session_state:
    st.session_state['halaman'] = "Overview"

if st.sidebar.button("Data Eksplorasi", use_container_width=True):
    st.session_state['halaman'] = "Data Eksplorasi"

if st.sidebar.button("Clustering Analysis", use_container_width=True):
    st.session_state['halaman'] = "Clustering Analysis"

menu = st.session_state['halaman']

# --- MAIN CONTENT ---

# HALAMAN 1: DATA EKSPLORASI
if menu == "Data Eksplorasi":
    st.title("Bike Sharing Data Dashboard")
    st.text("Selamat datang di dashboard analisis penyewaan sepeda.")
    st.markdown(f"**Menampilkan Data Untuk:** {pilihan_musim}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Penyewaan", f"{main_day_df['cnt'].sum():,.0f}")
    with col2:
        st.metric("Pelanggan Registered", f"{main_day_df['registered'].sum():,.0f}")
    with col3:
        st.metric("Pelanggan Casual", f"{main_day_df['casual'].sum():,.0f}")
        
    st.markdown("---")
    
    # PERTANYAAN 1: Pola penggunaan harian/mingguan (Weekday)
    st.subheader("Pola Penggunaan Sepeda Berdasarkan Hari")
    fig, ax = plt.subplots(figsize=(10, 5))
    weekday_grouped = main_day_df.groupby('weekday')['cnt'].sum().reset_index()
    max_weekday = weekday_grouped['cnt'].max()
    colors_weekday = ['#1f77b4' if val == max_weekday else '#d3d3d3' for val in weekday_grouped['cnt']]
    
    sns.barplot(x='weekday', y='cnt', data=weekday_grouped, palette=colors_weekday, ax=ax)
    ax.set_title("Total Penyewaan Berdasarkan Hari dalam Seminggu")
    ax.set_xlabel("Hari (0: Minggu - 6: Sabtu)")
    ax.set_ylabel("Total Sewa")
    st.pyplot(fig)

    # PERTANYAAN 2: Registered vs Casual 
    st.subheader("2. Perbandingan Jumlah Pengguna Casual vs Registered")
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Casual vs Registered 
    user_type_data = pd.DataFrame({
        'Tipe Pengguna': ['Casual', 'Registered'],
        'Total Users': [main_day_df['casual'].sum(), main_day_df['registered'].sum()]
    })
    
    sns.barplot(x='Tipe Pengguna', y='Total Users', data=user_type_data, palette=['#d3d3d3', '#1f77b4'], ax=ax)
    ax.set_title("Total Volume Penyewaan Berdasarkan Tipe Pengguna")
    ax.set_ylabel("Total Pengguna")
    ax.set_xlabel(None)
    
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,.0f}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        # PERTANYAAN 3: Pengaruh Musim
        st.subheader("Pengaruh Musim")
        fig, ax = plt.subplots(figsize=(8, 5))
        season_grouped = main_day_df.groupby('season')['cnt'].sum().reset_index()
        max_season = season_grouped['cnt'].max()
        colors_season = ['#1f77b4' if val == max_season else '#d3d3d3' for val in season_grouped['cnt']]
        
        sns.barplot(x='season', y='cnt', data=season_grouped, palette=colors_season, ax=ax)
        ax.set_title("Total Penyewaan Berdasarkan Musim")
        ax.set_xlabel("Musim (1:Spring, 2:Summer, 3:Fall, 4:Winter)")
        ax.set_ylabel("Total Sewa")
        st.pyplot(fig)
        
    with col2:
        # PERTANYAAN 5: Pengaruh Cuaca 
        st.subheader("Pengaruh Cuaca")
        fig, ax = plt.subplots(figsize=(8, 5))
        weather_grouped = main_day_df.groupby('weathersit')['cnt'].sum().reset_index()
        max_weather = weather_grouped['cnt'].max()
        colors_weather = ['#1f77b4' if val == max_weather else '#d3d3d3' for val in weather_grouped['cnt']]
        
        sns.barplot(x='weathersit', y='cnt', data=weather_grouped, palette=colors_weather, ax=ax)
        ax.set_title("Total Penyewaan Berdasarkan Cuaca")
        ax.set_xlabel("Cuaca (1:Cerah, 2:Mendung, 3:Hujan Ringan)")
        ax.set_ylabel("Total Sewa")
        st.pyplot(fig)

    # PERTANYAAN 4: Hari Kerja vs Libur
    st.subheader("Penggunaan Sepeda: Hari Kerja vs Hari Libur")
    fig, ax = plt.subplots(figsize=(8, 5))
    workday_grouped = main_day_df.groupby('workingday')['cnt'].sum().reset_index()
    max_workday = workday_grouped['cnt'].max()
    colors_workday = ['#1f77b4' if val == max_workday else '#d3d3d3' for val in workday_grouped['cnt']]
    
    sns.barplot(x='workingday', y='cnt', data=workday_grouped, palette=colors_workday, ax=ax)
    ax.set_title("Total Penyewaan (Hari Libur vs Hari Kerja)")
    ax.set_xlabel("Hari Kerja (0: Libur, 1: Hari Kerja)")
    ax.set_ylabel("Total Sewa")
    st.pyplot(fig)

    st.markdown("---")

    # PERTANYAAN 6: Pola per Jam (Sibuk vs Sepi) (Line Chart tetap garis biasa karena berkesinambungan)
    st.subheader("Pola Penggunaan Sepeda Berdasarkan Jam")
    fig, ax = plt.subplots(figsize=(16, 5))
    sns.lineplot(x='hr', y='cnt', data=main_hour_df, ax=ax, color='#1f77b4', errorbar=None)
    ax.set_title("Rata-rata Penyewaan Sepeda per Jam")
    ax.set_xlabel("Jam (0 - 23)")
    ax.set_ylabel("Rata-rata Sewa")
    st.pyplot(fig)

    # PERTANYAAN 7: Pola per Jam (Hari Kerja vs Libur)
    st.subheader("Pola Jam: Hari Kerja vs Libur")
    fig, ax = plt.subplots(figsize=(16, 5))
    sns.lineplot(x='hr', y='cnt', hue='workingday', data=main_hour_df, ax=ax, palette='Set1', errorbar=None)
    ax.set_title("Rata-rata Penyewaan per Jam Berdasarkan Hari Kerja")
    ax.set_xlabel("Jam (0 - 23)")
    ax.set_ylabel("Rata-rata Sewa")
    ax.legend(title='Hari Kerja', labels=['Hari Libur (0)', 'Hari Kerja (1)'])
    st.pyplot(fig)

# HALAMAN 2: CLUSTERING ANALYSIS
elif menu == "Clustering Analysis":
    st.title("Clustering Analysis")
    st.markdown(f"**Data difilter untuk:** {pilihan_musim}")
    
    if not main_day_df.empty and not main_hour_df.empty:
        # 1. Binning 
        main_day_df['Demand_Level'] = pd.qcut(main_day_df['cnt'], q=3, labels=['Low Demand', 'Medium Demand', 'High Demand'], duplicates='drop')
        demand_counts = main_day_df['Demand_Level'].value_counts().reset_index()
        demand_counts.columns = ['Demand_Level', 'Jumlah_Hari']
        demand_counts['Demand_Level'] = demand_counts['Demand_Level'].astype('str')
        demand_counts['Jumlah_Hari'] = demand_counts['Jumlah_Hari'].astype('int64')
        
        # 2. Manual Grouping 
        def categorize_time(hr):
            if 6 <= hr <= 9: return 'Morning Rush (06-09)'
            elif 10 <= hr <= 15: return 'Mid-Day (10-15)'
            elif 16 <= hr <= 19: return 'Evening Rush (16-19)'
            else: return 'Night/Early (20-05)'
            
        main_hour_df['Time_Group'] = main_hour_df['hr'].apply(categorize_time)
        time_group_avg = main_hour_df.groupby('Time_Group')['cnt'].mean().reset_index()
        time_group_avg.columns = ['Kategori_Waktu', 'Rata_rata_Sewa']
        time_group_avg['Kategori_Waktu'] = time_group_avg['Kategori_Waktu'].astype('str')
        time_group_avg['Rata_rata_Sewa'] = time_group_avg['Rata_rata_Sewa'].astype('float64')
        
        st.subheader("Tabel Hasil Clustering")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**1. Hasil Binning (Tingkat Permintaan)**")
            st.dataframe(demand_counts, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("**2. Hasil Manual Grouping (Jam Operasional)**")
            st.dataframe(time_group_avg, use_container_width=True, hide_index=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        max_demand = demand_counts['Jumlah_Hari'].max()
        colors_demand = ['#1f77b4' if val == max_demand else '#d3d3d3' for val in demand_counts['Jumlah_Hari']]
        sns.barplot(x='Demand_Level', y='Jumlah_Hari', data=demand_counts, ax=axes[0], palette=colors_demand)
        axes[0].set_title('Binning: Distribusi Hari')
        
        max_time = time_group_avg['Rata_rata_Sewa'].max()
        colors_time = ['#1f77b4' if val == max_time else '#d3d3d3' for val in time_group_avg['Rata_rata_Sewa']]
        sns.barplot(x='Kategori_Waktu', y='Rata_rata_Sewa', data=time_group_avg, ax=axes[1], palette=colors_time)
        axes[1].set_title('Manual Grouping: Sewa per Waktu')
        plt.xticks(rotation=15)
        
        st.pyplot(fig)
    else:
        st.warning(f"Tidak ada data transaksi penyewaan pada {pilihan_musim}.")
