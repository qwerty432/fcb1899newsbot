from bs4 import BeautifulSoup
import requests
from selenium import  webdriver


#download image by url to 'images' folder
def download_image(url, name) :
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open('images/' + name, 'wb') as f:
            f.write(r.content)

#prepare image for inserting to Instant View
def prepare_image(path):
    with open(path, 'rb') as f:
        new_path = requests.post(
                'http://telegra.ph/upload', files={'file': 
                                                    ('file', f, 
                                                    'image/jpeg')}).json()
    return new_path[0]['src']



#dict for endings (1 day, 3 days etc.)
endings = {'days': 's', 'hours': 's', 'mins': 's'}


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
def parse_article(url) :
    instant_view = ''
    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    article = soup.find_all('article')[0]

    # title = soup.find('article.intro')[0]

    # article_photo_url = soup.find('.article-photo').find('img')['src']

    # image_name = article_photo_url.split('/')[-1]
    # download_image(article_photo_url, image_name)

    paragraphs = article.find_all('p')[1:]


    for p in paragraphs :
        if 'img' in str(p) :
            image_url = p.find('img')['src']
            image_name = image_url.split('/')[-1]


            download_image(image_url, image_name)

            p = str(p)
            new_path = prepare_image('images/{}'.format(image_name))
            p = '<p><img src="{}"/></p'.format(new_path)


        instant_view += str(p)
    return instant_view

