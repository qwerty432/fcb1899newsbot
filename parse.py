from bs4 import BeautifulSoup
import requests
from selenium import  webdriver


#dict for endings (1 day, 3 days etc.)
endings = {'days': 's', 'hours': 's', 'mins': 's'}


#download image by url to 'images' folder
def download_image(url, name) :
    print("Downloading image...")
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




#parse remaining time before next match
def parse_time() :
    url = "https://www.fcbarcelona.com/"
    # page = requests.get(url)

    driver = webdriver.Firefox()    
    driver.get(url)
    

    page = driver.page_source
    soup = BeautifulSoup(page, 'lxml')

    time_left = soup.find('p', class_='matches__countdown')

    days_left = time_left.find('span', id = 'days').text
    hours_left = time_left.find('span', id = 'hours').text
    minutes_left = time_left.find('span', id = 'mins').text


    if int(days_left) == 1 :
        endings['days'] = ''
    elif int(hours_left) == 1 :
        endings['hours'] = ''
    elif int(minutes_left) == 1 :
        endings['mins'] = ''

    print(endings['days'])

    time = "Time to next match: {} day{}, {} hour{} {} minute{}".\
        format(days_left, endings['days'], hours_left, \
                endings['hours'], minutes_left, endings['mins'])
    print(time)

    return time



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



#creates Instant View on telegra.ph
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



#parse newest event related to Barca
def parse_latest_news(url) :
    urls = []
    flag = False
    keywords = ['Барселона', 'Вальверде', 'Месси', 'Неймар', 'Суарес', \
                'Иньеста', 'Букскетс', 'Дембеле', 'Коутиньо', 'Паулиньо', \
                'Тер Стеген', 'Альба', 'Пике', 'Умтити', 'Роберто', 'Гомеш', \
                'Бартомеу', 'Каталония', 'Камп Ноу', 'Силессен', 'Мина', \
                'Видаль', 'Динь', 'Семеду', 'Вермален', 'Денис Суарес',\
                'Денис', 'Ракитич', 'Алькасер', 'Пако', 'Арнаис']

    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    news = soup.find('section', class_='news-archive')

    other_news = news.find('ul', class_='archive-list').find_all('li')
    
    for article in other_news :
        title = article.find('h4').find('a')
        url = title['href']
        short_descr = article.find('a', class_='intro-text')
        for keyword in keywords :
            if keyword in str(title) or keyword in str(short_descr) :
                flag = True
                urls.append(url)

    return urls[0]


#returns Instant View of newest event
def get_latest_news() : 
    url = 'http://football.ua/news/archive/spain/'
    article_url = parse_latest_news(url)

    instant_view_urls = create_instant_view(article_url)

    return instant_view_urls