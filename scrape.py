from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import requests
import pandas as pd
import os

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

def scrape_detik(query, start_date, end_date):
  file_name = query.lower().replace(" ", "_")
  file_path = f"{file_name}.csv"
  file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0
  last_page = detik_page(query, start_date, end_date)

  with open(f"{file_name}.csv", mode="a", newline="", encoding="utf-8") as csv_file:
    fieldnames = ["title", "url", "date"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if not file_exists:
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

if __name__ == '__main__':
    queries = ['Gempa NTT', 'Karhutla']
    
    today = datetime.now()
    day = today - timedelta(days=1)
    start_date = day.strftime('%d/%m/%Y')
    end_date = day.strftime('%d/%m/%Y')

    for query in queries:
        scrape_detik(query, start_date, end_date)
