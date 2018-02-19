from bs4 import BeautifulSoup
import requests
from selenium import  webdriver


#download image by url to 'image' folder
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
    return new_path



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



if __name__ == '__main__':
     parse_time()