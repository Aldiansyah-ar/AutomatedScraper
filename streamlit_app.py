import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="News Dashboard", layout="wide")
st.title("News Count Visualization")

def counts(df):
    if 'date' not in df.columns:
        st.error("Cannot find date feature.")
        return None

    df['date_clean'] = df['date'].astype(str).str.extract(r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})')
    month_map = {
        'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Apr', 
        'Mei': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Agu': 'Aug', 
        'Agt': 'Aug', 'Sep': 'Sep', 'Okt': 'Oct', 'Nov': 'Nov', 'Des': 'Dec'
    }
    for indo, eng in month_map.items():
        df['date_clean'] = df['date_clean'].str.replace(indo, eng, regex=False)

    df['parsed_date'] = pd.to_datetime(df['date_clean'], format='%d %b %Y', errors='coerce')
    daily_counts = df.groupby('parsed_date').size().reset_index(name='jumlah_berita')
    daily_counts = daily_counts.sort_values('parsed_date')
    return daily_counts

def plot_counts(title, daily_counts):
    fig, ax = plt.subplots(figsize=(12, 5)) 
    ax.plot(
        daily_counts['parsed_date'], 
        daily_counts['jumlah_berita'], 
        marker='o', 
        markersize=4, 
        color='#1f77b4', 
        linewidth=1.5,
        label='Source: detiknews.com'
    )
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right', frameon=True, fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

st.sidebar.header("Data Settings")
DATA_DIR = "./"

# Pencarian file CSV secara rekursif
csv_files = glob.glob(os.path.join(DATA_DIR, "**", "*.csv"), recursive=True)

if csv_files:
    # Mengelompokkan file berdasarkan foldernya masing-masing
    folder_dict = {}
    for f in csv_files:
        rel_path = os.path.relpath(f, DATA_DIR)
        folder_name = os.path.dirname(rel_path)
        if folder_name == "":
            folder_name = "(Root)"
        if folder_name not in folder_dict:
            folder_dict[folder_name] = []
        folder_dict[folder_name].append(f)
        
    folders = sorted(list(folder_dict.keys()))
    
    # 1. Pilih Folder terlebih dahulu
    selected_folder = st.sidebar.selectbox("Pilih Folder:", folders)
    
    # 2. Pilih File CSV berdasarkan folder yang aktif
    files_in_folder = folder_dict[selected_folder]
    file_names = [os.path.basename(f) for f in files_in_folder]
    selected_file_name = st.sidebar.selectbox("Pilih File CSV:", file_names)
    
    # Ambil path lengkap file yang dipilih
    selected_file_path = next(f for f in files_in_folder if os.path.basename(f) == selected_file_name)
    df = pd.read_csv(selected_file_path)
    
    daily_counts = counts(df)
    
    if daily_counts is not None and not daily_counts.empty:
        daily_counts = daily_counts.dropna(subset=['parsed_date'])
        
        min_date = daily_counts['parsed_date'].min().date()
        max_date = daily_counts['parsed_date'].max().date()
        
        st.sidebar.markdown("---")
        st.sidebar.header("Filter Tanggal")
        
        selected_date_range = st.sidebar.date_input(
            "Pilih Rentang Tanggal",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
            mask = (daily_counts['parsed_date'].dt.date >= start_date) & (daily_counts['parsed_date'].dt.date <= end_date)
            filtered_counts = daily_counts.loc[mask].copy()
        else:
            filtered_counts = daily_counts.copy()

        if not filtered_counts.empty:
            col1, col2 = st.columns(2)
            col1.metric(label="Total Count", value=int(filtered_counts['jumlah_berita'].sum()))
            col2.metric(label="Total Day", value=len(filtered_counts))
            
            plot_counts(f"News Trend ({selected_file_name})", filtered_counts)
            
            filtered_counts['parsed_date'] = filtered_counts['parsed_date'].dt.strftime('%Y-%m-%d')
            csv_data = filtered_counts.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download Data CSV (Filtered)",
                data=csv_data,
                file_name=f"filtered_news_count_{selected_file_name}",
                mime="text/csv",
            )
        else:
            st.warning("Tidak ada data pada rentang tanggal yang dipilih.")
    else:
        st.warning("Date data invalid.")
else:
    st.sidebar.warning(f"No CSV file in `{DATA_DIR}` folder or subfolders.")