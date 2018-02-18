from bs4 import BeautifulSoup
import requests
from selenium import  webdriver


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


    time = "Time to next match: {} days, {} hours {} minutes".\
        format(days_left, hours_left, minutes_left)
    print(time)

    return time



if __name__ == '__main__':
     parse_time()