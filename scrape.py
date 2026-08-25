from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import requests
import pandas as pd
import matplotlib.pyplot as plt

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def detik_page(query, start_date, end_date):
  url = f'https://www.detik.com/search/searchnews?query={query}&siteid=3&sortby=time&sorttime=1&fromdatex={start_date}&todatex={end_date}&result_type=latest'
  text = requests.get(url, user_agent).text
  sop = BeautifulSoup(text, 'lxml')
  try:
    paging = sop.find_all('div','pagination text-center mgt-16 mgb-48')[0].find_all('a')[-2]
    last_page = paging.text
  except:
    last_page = 1
  return last_page

def scrape_detik():
  query = 'Gempa NTT'
  today = datetime.now()
  day = today - timedelta(days=2)
  start_date = day.strftime('%d/%m/%Y')
  end_date = day.strftime('%d/%m/%Y')

  file_name = 'gempantt'
  last_page = detik_page(query, start_date, end_date)

  with open(f"{file_name}.csv", mode="a", newline="", encoding="utf-8") as csv_file:
    fieldnames = ["title", "url", "date"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for page in range(1, int(last_page) + 1):
      url = f"https://www.detik.com/search/searchnews?query={query}&siteid=3&sortby=time&sorttime=1&fromdatex={start_date}&todatex={end_date}&result_type=latest&page={page}"
      text = requests.get(url, user_agent).text
      soup = BeautifulSoup(text, "lxml")
      articles_container = soup.find_all("article", class_="list-content__item")
      print(f"page: {page}")

      for article in articles_container:
        headline = article.find("div", "media__text").find("a").text
        link = article.find("div", "media__text").find("a")["href"]
        date = article.find("div", "media__date").text
        writer.writerow({"title": headline, "url": link, "date": date})

  df = pd.read_csv(f'{file_name}.csv')
  regex_pattern = r'^https?:\/\/20\.detik\.com'
  df_cleaned = df[~df['url'].str.contains(regex_pattern, regex=True, na=False)]
  df_cleaned.to_csv(f'{file_name}.csv', index=False)

def generate_visualization():
    file_name = 'gempantt'
    df = pd.read_csv(f'{file_name}')
    df['date_clean'] = df['date'].str.extract(r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})')

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

    title = 'News Count'
    plt.figure(figsize=(12, 5))
    plt.plot(
        daily_counts['parsed_date'], 
        daily_counts['jumlah_berita'], 
        marker='o', 
        markersize=3, 
        color='#1f77b4', 
        linewidth=1.5,
        label='Source: detiknews.com'
    )
    plt.title(f'{title}', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Count', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper right', frameon=True, fontsize=10)
    plt.tight_layout()

    output_image = 'news_count.png'
    plt.savefig(output_image, dpi=300)
    plt.close()

if __name__ == '__main__':
    scrape_detik()
    generate_visualization()
