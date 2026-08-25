from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import requests

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
  yesterday = today - timedelta(days=1)
  start_date = today.strftime('%d/%m/%Y')
  end_date = today.strftime('%d/%m/%Y')

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

if __name__ == '__main__':
  scrape_detik()