from bs4 import BeautifulSoup
import requests
from selenium import  webdriver


#dict for endings (1 day, 3 days etc.)
ending_s_dict = {'days': 's', 'hours': 's', 'mins': 's'}


#function to parse remaining time before next match
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
        ending_s_dict['days'] = ''
    elif int(hours_left) == 1 :
        ending_s_dict['hours'] = ''
    elif int(minutes_left) == 1 :
        ending_s_dict['mins'] = ''

    print(ending_s_dict['days'])

    time = "Time to next match: {} day{}, {} hour{} {} minute{}".\
        format(days_left, ending_s_dict['days'], hours_left, \
                ending_s_dict['hours'], minutes_left, ending_s_dict['mins'])
    print(time)

    return time



if __name__ == '__main__':
     parse_time()