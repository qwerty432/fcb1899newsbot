# -*- coding: utf-8 -*-
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from telegraph import Telegraph
from telegraph.exceptions import TelegraphException
from config import teletoken
import json
import users_controller
import flag
import keyboards
from useful_dictionaries import CHAMPIONATS_DICT
from googletrans import Translator
from languages import LANG_DICT
import bot_methods

translator = Translator()


def get_team_foot_url(user):
    url = CHAMPIONATS_DICT[user.language][user.champ]
    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    if user.language == 'ru':
        team_name = user.team
    else:
        team_name = bot_methods.get_users_teams(user.id)[user.team]

    team_url = [team['href'] for team in soup.find('section', class_='top-teams').find_all('a') if team.find('img')['alt'] == team_name][0]

    return team_url


# parses all information about next match
def parse_match(champ_name, team_name, user_id, lang=None, match='next'):
    user = users_controller.get_user(user_id)
    url = get_team_foot_url(user)

    if match == 'next':
        table_num = 1
        match_index = 0
    else:
        table_num = 0
        match_index = -2

    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    match = {}

    # scrapes next matches table
    try:
        matches = soup.find_all('table', class_='feed-table')[table_num]\
                           .find_all('tr')
    except IndexError:
        return None

    match_where = [' '.join(part.split()) for part in matches[match_index].find('p').get_text().split('\n')[1:-1]]

    match['date'] = match_where[0]
    match['tournament'] = match_where[1]
    match['stage'] = match_where[2]

    #  scrapes info about home and guest teams and time of the match
    match['time'] = matches[1].find_all('td')[0].get_text()
    match['home'] = ' '.join(matches[match_index + 1].find_all('td')[1].get_text().split())
    match['guest'] = ' '.join(matches[match_index + 1].find_all('td')[3].get_text().split())
    match['score'] = ' '.join(matches[match_index + 1].find_all('td')[2].get_text().split())

    for key in match:
        if key in ['tournament', 'stage', 'home', 'guest'] and lang == 'ua':
            match[key] = translator.translate(match[key], 'uk').text

    return match


# parse remaining time before next match
def parse_time(user):
    next_match = parse_match(user.champ, user.team, user.id, match='next')

    if not next_match:
        return LANG_DICT[user.language]['uknown_match_date_msg']

    date, time = next_match['date'], next_match['time']

    day = int(date.split('.')[0])
    month = int(date.split('.')[1])
    year = int(date.split('.')[2])

    try:
        hours = int(time.split(':')[0])
        minutes = int(time.split(':')[1])
    except ValueError:
        return LANG_DICT[user.language]['uknown_match_time_msg']

    now = datetime.now()    # exact time when request made
    match_date = datetime(year, month, day, hours, minutes, 0)

    time_left = match_date - now    # calculate remaining time

    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60

    return time_left.days, hours, minutes


# function for parsing article
def parse_article(url, too_big=False):
    content = ''
    page = requests.get(url)
    url = page.url

    html = page.text

    soup = BeautifulSoup(html, 'lxml')
    article = soup.find_all('article')[0]

    title = article.find_all('h1')[0].text  # title of article
    paragraphs = article.find_all('p')[1:]  # all useful text from article

    header = article.find('div', class_='news-header-top')
    if header:
        img = header.find('img')
        if img:
            content += "<img src='{}'></img>".format('/'.join(url.split('/')[:3]) + img['src'])

    for p in paragraphs:
        if 'class="intro"' in str(p):  # get article photo
            try:
                image_url = article.find('div', class_='article-photo').find('img')['src']
                content += "<img src='{}'></img>".format(image_url)
            except:
                print('No article photo')
            content += p.get_text()

        elif 'img' in str(p):
            image_url = p.find('img')['src']    # get image's url
            content += "<img src='{}'></img>".format(image_url)    # create image path appr. for Telegraph

        elif('span' not in str(p)):  # 'span' tag is not allowed in telegraph
            content += str(p)

    # if article is too big we split it into two different Instant Views
    if too_big:
        content_list = content.split('<p')  # split all paragraphs
        middle = int(len(content_list) / 2)  # middle of all paragraphs

        content1 = '<p'.join(content_list[:middle])  # first page

        content_list[middle] = '<p' + content_list[middle]
        content2 = '<p'.join(content_list[middle:])  # second page

        titles = [title + '. Part1', title + '. Part2']  # titles for 2 pages
        content = [content1, content2]

        return titles, content

    return title, content


# function for creating Instant View
def create_instant_view(url):
    telegraph = Telegraph(teletoken)
    title, content = parse_article(url)

    try:
        response = telegraph.create_page(title=title, html_content=content)
        return response['url']  # url of created telegraph page

    except TelegraphException:  # if article is too big
        print("Oh no, something went wrong.")
        titles, contents = parse_article(url, too_big=True)

        response1 = telegraph.create_page(title=titles[0],
                                          html_content=contents[0])
        response2 = telegraph.create_page(title=titles[1],
                                          html_content=contents[1])
        # urls of created telegraph pages
        return [response1['url'], response2['url']]


# parses latest news
def send_news(self, user_id, lang):
    titles = []
    urls = []
    all_news = {}

    user = users_controller.get_user(user_id)

    url = get_team_foot_url(user)

    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    news = soup.find('article', class_='news-feed')

    try:
        other_news = news.find('ul').find_all('li', attrs={'class': None})[:10]

        for article in other_news:
            titles.append(article.find('a').get_text())
            urls.append(article.find('a')['href'])
            all_news['titles'] = titles
            all_news['urls'] = urls

        self.bot.send_message(user_id, LANG_DICT[lang]['last_news_msg'],
                              reply_markup=keyboards.set_news_buttons(user_id, all_news))
    except:
        self.bot.send_message(user_id, LANG_DICT[lang]['no_news_msg'])


# parses articles
def send_articles(self, user_id, lang):
    titles = []
    urls = []
    all_articles = {}

    user = users_controller.get_user(user_id)

    url = get_team_foot_url(user)

    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    articles_block = soup.find('ul', class_='archive-list')

    try:
        articles = articles_block.find_all('li')

        for article in articles:
            titles.append(article.find('h4').find('a').get_text())
            urls.append(article.find('h4').find('a')['href'])

        all_articles['titles'] = titles
        all_articles['urls'] = urls

        self.bot.send_message(user_id, LANG_DICT[lang]['articles_msg'],
                              reply_markup=keyboards.set_news_buttons(user_id, all_articles))

    except:
        self.bot.send_message(user_id, LANG_DICT[lang]['no_articles_msg'])


# gives list of teams
def get_teams_list(user_id):
    user = users_controller.get_user(user_id)
    url = CHAMPIONATS_DICT[user.language][user.champ]

    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    teams = [team['alt'] for team in soup.find('section', class_='top-teams').find_all('img')]

    translated_teams = [team for team in translator.translate('\n'.join(teams), src='ru', dest='uk').text.split('\n')]
    data = dict(zip(translated_teams, teams))
    with open('{}_teams.json'.format(user_id), 'w') as file:
        json.dump(data, file)

    if user.language == 'ru':
        return teams
    else:
        return translated_teams


# gives team's squad
def get_teams_squad(user_id):
    user = users_controller.get_user(user_id)
    url = get_team_foot_url(user)
    countries_dict = bot_methods.get_countries_dict()
    lang = user.language

    message_text = ''
    squad_positions = LANG_DICT[lang]['positions']

    page = requests.get(url)
    html = page.text

    soup = BeautifulSoup(html, 'lxml')

    squad_block = soup.find('article', class_='team-consist')

    if not squad_block:
        return LANG_DICT[lang]['no_squad_msg']

    for i, position_table in enumerate(squad_block.find_all('table', class_='consist-table')):
        message_text += squad_positions[i]

        footballers = position_table.find_all('tr')
        country_emoji = ''

        footballer_names_str = '\n'.join([footballer.find('td', class_='num').get_text()
                                          + '. '
                                          + footballer.find('a').get_text() for footballer in footballers])
        if lang == 'ua':
            translated_names = translator.translate(footballer_names_str, src='ru', dest='uk').text.split('\n')
        else:
            translated_names = footballer_names_str.split('\n')

        for trans_footballer in translated_names:
            num = trans_footballer.split('.')[0]
            name = trans_footballer.split('.')[1].strip()
            footballer = [footballer for footballer in footballers if footballer.find('td', class_='num').get_text() == num][0]
            try:
                birth_date = footballer.find('td', class_='birth').find('p').get_text()
            except:
                birth_date = LANG_DICT[lang]['not_mentioned_str']
            country_name = footballer.find('img')['alt']

            for key in countries_dict:
                if countries_dict[key] == country_name:
                    country_code = key
                    country_emoji = flag.flagize(':{}:'.format(country_code))

            message_text += '{}. {} {} (_{}_)\n'.format(num, country_emoji, name, birth_date)
        message_text += '\n'

    return message_text
