# news web scrapper
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd

# scrap weather news articles from the web (from a popular website like nasa)
# get the relevant html tags as text
# integrate the scrapped html tags into our system


def scrapper():
    # website url to be scrapped
    url = "https://www.aljazeera.com/climate-crisis/"

    # getting the url request
    url_request = requests.get(url)

    # storing the request
    website_coverpage = url_request.content

    # the soup element to enable web scrapping
    website_soup = BeautifulSoup(website_coverpage, 'html.parser')

    # locating the elements needed
    coverpage_news = website_soup.find_all('article', class_="gc u-clickable-card gc--type-post gc--list gc--with-image")


    # number of articles to be displayed
    number_of_articles = len(coverpage_news)

    # the content, links and titles
    list_links = []
    list_titles = []
    news_img_links = []
    news_content = []

    for n in np.arange(0, number_of_articles):
        if "live" in coverpage_news:
            continue

        # getting the link of the articles
        link = coverpage_news[n].find('a')['href']
        full_link = "https://www.aljazeera.com" + link
        list_links.append(full_link)

        # getting the image news links
        img = coverpage_news[n].find('img')['src']
        img_link = "https://www.aljazeera.com" + img
        news_img_links.append(img_link)

        # getting the titles
        title = coverpage_news[n].find('a').get_text()
        list_titles.append(title)

        # getting the full text content of the page
        # once the ('a')['href'] link is clicked
        # reading the content (divided into paragraphs)
        article = requests.get(full_link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, "html.parser")
        # searching for paragraphs
        main_body = soup_article.find('div', class_='l-col l-col--8').find_all('p')

        # unifying the paragraphs
        list_paragraphs = []
        for p in np.arange(0, len(main_body)):
            list_paragraphs.append(main_body[p].get_text())
            final_article = " ".join(list_paragraphs)
        news_content.append(final_article)

    # binding the title, links and image links for each content
    # in a pandas dataframe
    data_features = pd.DataFrame (
        {
            'Article Title': list_titles,
            'Article Links': list_links,
            'Article Image Links': news_img_links,
            'Article Content': news_content
        }
    )

    return list_titles,list_links,news_img_links,news_content