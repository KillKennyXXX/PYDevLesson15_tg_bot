from csv import DictWriter
from bs4 import BeautifulSoup
from requests import get

url = f'https://habr.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
def get_news():
    res = get(url + '/ru/news', headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    return [tag['href'] for tag in soup.find_all('a', class_='tm-article-snippet__readmore') if 'company' not in tag['href']]


def write_news(news):
    with open('base.csv', mode='w', encoding='utf8') as f:
        tt = DictWriter(f, fieldnames=['date', 'avtor', 'title', 'link', 'img', 'text'], delimiter=';')
        tt.writeheader()
        [tt.writerow(new) for new in news]

def read_news(news_url):
    news_list = []
    for new in news_url:
        row = {}

        res = get(url + new, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find_all('span', class_='')
        row['title'] = title[0].text
        row['link'] = url + new

        date = soup.find_all('time')
        date = date[0]
        row['date'] = date['title']

        avtor = soup.find_all('a', class_='tm-user-info__username')
        row['avtor'] = avtor[0].text.replace('\n', '').replace(' ', '')

        img = soup.find_all('img', class_='')
        img = img[0]
        row['img'] = img['src'] if '.jpeg' in img['src'] or '.jpg' in img['src'] or '.png' in img['src'] else ''
        text = ''
        for tag in soup.find_all('p', class_=''):
            text += tag.text
        row['text'] = text
        news_list.append(row)
    return news_list

def read_new(news_url, num):
    row = {}
    new = news_url[num]
    res = get(url + new, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.find_all('span', class_='')
    row['title'] = title[0].text
    row['link'] = url + new

    date = soup.find_all('time')
    date = date[0]
    row['date'] = date['title']

    avtor = soup.find_all('a', class_='tm-user-info__username')
    row['avtor'] = avtor[0].text.replace('\n', '').replace(' ', '')

    img = soup.find_all('img', class_='')
    img = img[0]
    row['img'] = img['src'] if '.jpeg' in img['src'] or '.jpg' in img['src'] or '.png' in img['src'] else ''
    text = ''
    for tag in soup.find_all('p', class_=''):
        text += tag.text
    row['text'] = text
    return row

if __name__ == '__main__':
    urls = get_news()
    news = read_new(urls, 0)
    print(news)
    # [print(new) for new in news]
    # write_news(news)


