# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from selenium import  webdriver
from constants import teletoken
from telegraph import Telegraph
from telegraph.exceptions import TelegraphException
from datetime import datetime, date


months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 
            'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
            'November': 11, 'December': 12,}


#dict for endings (1 day, 3 days etc.)
endings = {'days': 's', 'hours': 's', 'mins': 's'}



def parse_next_match(parameter) :

    url = "http://football.ua/club/51-barcelona.html"
    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')


    next_matches = soup.find_all('table', class_='feed-table')[1].find_all('tr')
    next_match_where = next_matches[0].find('p').text.replace(' ', '').replace('\r', '').split('\n')[1:-1]
    next_match_date = next_match_where[0]
    next_match_tournament = next_match_where[1]
    next_match_stage = next_match_where[2]


    next_match_time = next_matches[1].find_all('td')[0].text
    next_match_home = next_matches[1].find_all('td')[1].text.replace(' ', '').replace('\n', '')
    next_match_guest = next_matches[1].find_all('td')[3].text.replace(' ', '').replace('\n', '')

    if parameter == 'time' :
        return next_match_date, next_match_time
    elif parameter == 'info' :
        return next_match_home, next_match_guest, next_match_tournament, \
                next_match_stage, next_match_date, next_match_time



#download image by url to 'images' folder
def download_image(url, name) :
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open('images/' + name, 'wb') as f:
            f.write(r.content)

#makes new path of image for inserting to Instant View
def make_path(path):
    with open(path, 'rb') as f:
        new_path = requests.post(
                'http://telegra.ph/upload', files={'file': 
                                                    ('file', f, 
                                                    'image/jpeg')}).json()
    return new_path[0]['src']


#prepares image
def prepare_image(p, image_url) :
    image_name = image_url.split('/')[-1]

    download_image(image_url, image_name)

    p = str(p)
    new_path = make_path('images/{}'.format(image_name))
    p = '<img src="{}"/>'.format(new_path)
    return p



#parse info about next match
def parse_info() :
    info = parse_next_match('info')

    home = info[0]
    guest = info[1]

    tournament = info[2]
    stage = info[3]

    date = info[4]

    time = info[5]

    return "📌 Следующий матч:\n⚽{} — {}\n🏆{}, {}\n📅{}, {}".format(home, guest,\
                                tournament, stage, date, time)


#parse remaining time before next match
def parse_time() :
    date, time = parse_next_match('time')
    day = int(date.split('.')[0])
    month = int(date.split('.')[1])
    year = int(date.split('.')[2])

    hours = int(time.split(':')[0])
    minutes = int(time.split(':')[1])

    now = datetime.now()
    match_date = datetime(year, month, day, hours, minutes, 0)

    time_left = match_date - now


    # if int(days_left) == 1 :
    #     endings['days'] = ''
    # elif int(hours_left) == 1 :
    #     endings['hours'] = ''
    # elif int(minutes_left) == 1 :
    #     endings['mins'] = ''

    # print(endings['days'])

    # time = "Time to next match: {} day{}, {} hour{} {} minute{}".\
    #     format(days_left, endings['days'], hours_left, \
    #             endings['hours'], minutes_left, endings['mins'])
    # print(time)

    return time_left



#function for parsing article
def parse_article(url, too_big=False) :
    content = ''
    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')
    article = soup.find_all('article')[0]
    
    title = article.find_all('h1')[0].text
    paragraphs = article.find_all('p')[1:]


    for p in paragraphs :
        if 'img' in str(p) :
            image_url = p.find('img')['src']
            p = prepare_image(p, image_url)

        if('span' not in str(p)) :
            content += str(p)     


        if 'class="intro"' in str(p) :
            image_url = article.find('div', class_='article-photo').\
                                            find('img')['src']
            p = prepare_image(p, image_url)
            content += str(p)

    
    #if article is too big we split it into two different Instant Views
    if(too_big) :
        content_list = content.split('<p')
        print(len(content_list))


        middle = int(len(content_list) / 2)

        content1 = '<p'.join(content_list[:middle])
        
        content_list[middle] = '<p' + content_list[middle]
        content2 = '<p'.join(content_list[middle:])


        print(content2)

        titles = [title + '. Part1', title + '. Part2']
        content = [content1, content2]

        return titles, content




    return title, content



def create_instant_view(url) :
    telegraph = Telegraph(teletoken)
    too_big = False
    
    title, content = parse_article(url)

    try :
        response = telegraph.create_page(title=title, html_content=content)
        return response['url']

    except TelegraphException :
        print("Oh no, something went wrong.")
        titles, contents = parse_article(url, too_big=True)    

        response1 = telegraph.create_page(title=titles[0], html_content=contents[0])
        response2 = telegraph.create_page(title=titles[1], html_content=contents[1])

        return [response1['url'], response2['url']]





def parse_latest_news() :
    all_news = []
    page_num = 1
    titles = []
    urls = []

    keywords = ['Барселона', 'Вальверде', 'Месси', 'Неймар', 'Суарес', \
                'Иньеста', 'Букскетс', 'Дембеле', 'Коутиньо', 'Паулиньо', \
                'Тер Стеген', 'Альба', 'Пике', 'Умтити', 'Роберто', 'Гомеш', \
                'Бартомеу', 'Каталония', 'Камп Ноу', 'Силессен', 'Мина', \
                'Видаль', 'Динь', 'Семеду', 'Вермален', 'Денис Суарес',\
                'Денис', 'Ракитич', 'Алькасер', 'Пако', 'Арнаис', 'Анонс', 'Итоги']

    while(len(urls) < 10) :
        main_url = 'http://football.ua/news/archive/spain/page{}.html'.format(page_num)


        page = requests.get(main_url)
        html = page.text



        soup = BeautifulSoup(html, 'lxml')

        news = soup.find('section', class_='news-archive')

        other_news = news.find('ul', class_='archive-list').find_all('li')
        
        for article in other_news :
            flag = False
            title = article.find('h4').find('a')
            url = title['href']

            short_descr = article.find('a', class_='intro-text')
            
            for keyword in keywords :
                if keyword in str(title)and not flag and len(urls) < 10:
                    urls.append(url)
                    titles.append(title.text)

                    flag = True

        page_num += 1

    all_news.append(titles)
    all_news.append(urls)

    return all_news

