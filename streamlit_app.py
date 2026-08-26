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
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

if csv_files:
    file_names = [os.path.basename(f) for f in csv_files]
    selected_file_name = st.sidebar.selectbox("Pilih File CSV:", file_names)
    selected_file_path = os.path.join(DATA_DIR, selected_file_name)
    df = pd.read_csv(selected_file_path)
    daily_counts = counts(df)
    if daily_counts is not None and not daily_counts.empty:
        col1, col2 = st.columns(2)
        col1.metric(label="Total Count", value=int(daily_counts['jumlah_berita'].sum()))
        col2.metric(label="Total Day", value=len(daily_counts))
        plot_counts(f"News Trend ({selected_file_name})", daily_counts)
        with st.expander("Detail"):
            st.dataframe(daily_counts, use_container_width=True)
    else:
        st.warning("Date data invalid.")
else:
    st.sidebar.warning(f"No CSV file in `{DATA_DIR}` folder.")