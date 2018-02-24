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
    url = "http://www.skysports.com/barcelona"
    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')


    next_match = soup.find('div', class_='matches-block__match-list')
    next_match_date = next_match.find_all('h4',class_='matches__group-header')\
                            [3].text
    time = next_match.find_all('ul', class_='matches__group')[3].\
                        find('span', class_='matches__date').text


    hours = time.split(':')[0][-2:]
    minutes = time.split(':')[1][:2]
    
    words = next_match_date.split(' ')
    day = words[1][:-2]
    month = months[words[2]]

    match_date = datetime(2018, month, int(day), int(hours), int(minutes), 0)
    today = datetime.now()

    time_left = match_date - today

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



#parse newest 10 events related to Barca
def parse_latest_news(url) :
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
        
        print(main_url)

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

