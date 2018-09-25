import json
import parse
from languages import LANG_DICT
import users_controller
from datetime import datetime
from useful_dictionaries import CHAMPIONATS_DICT


# get countries dict with countries' flags
def get_countries_dict():
    with open('country.json', 'r') as file:
        data = json.load(file)

    return data


# get teams of user's chosen championat with translations
def get_users_teams(user_id):
    with open('{}_teams.json'.format(user_id)) as file:
        data = json.load(file)

    return data


# gives general information about next match
def get_match_info(user, match_type='next'):
    lang = user.language
    match = parse.parse_match(user.champ, user.team, user.id, lang, match_type)

    if match_type == 'next':
        match_string = LANG_DICT[lang]['next_match_msg']
    else:
        match_string = LANG_DICT[lang]['last_match_msg']

    if match is not None:
        message_text = "📌 *{} матч*\n⚽ {} {} {}\n🏆 {}, {}\n📅 {}, {}"\
                                    .format(match_string, match['home'],
                                            match['score'], match['guest'],
                                            match['tournament'],
                                            match['stage'], match['date'],
                                            match['time'])
    else:
        message_text = LANG_DICT[lang]['uknown_match_date_msg']

    return message_text


# gives right endings for different numbers
def get_endings(lang, *values):
    endings = []
    ENDINGS_DICT = LANG_DICT[lang]['endings']

    for i, value in enumerate(values):
        remainder = value % 10
        if remainder == 1:
            if i == 0:
                endings.append(ENDINGS_DICT['left_message'][0])
            endings.append(ENDINGS_DICT['values_end_with_1'][i])
        elif remainder in range(2, 5):
            if i == 0:
                endings.append(ENDINGS_DICT['left_message'][1])
            endings.append(ENDINGS_DICT['values_end_with_234'][i])
        else:
            if i == 0:
                endings.append(ENDINGS_DICT['left_message'][1])
            endings.append(ENDINGS_DICT['other_values'][i])

    return endings


def send_time_to_match(bot, user):
    days, hours, minutes = parse.parse_time(user)
    endings = get_endings(user.language, days, hours, minutes)

    message_text = '{} {} {} {}, {} {}, {} {}'.format(LANG_DICT[user.language]['time_to_match_msg'],
                                                      endings[0],
                                                      days, endings[1],
                                                      hours, endings[2],
                                                      minutes, endings[3])

    bot.send_message(user.id, message_text)


# updates name of team and champ while changing the language
def update_names(user, updated_lang):
    data = get_users_teams(user.id)

    if updated_lang == 'ua':
        users_controller.set_champ(user.id, [champ for champ in CHAMPIONATS_DICT['ua'].keys() if CHAMPIONATS_DICT['ru'][user.champ] == CHAMPIONATS_DICT['ua'][champ]][0])
        users_controller.set_team(user.id, [team for team in data.keys() if user.team == data[team]][0])
    else:
        users_controller.set_champ(user.id, [champ for champ in CHAMPIONATS_DICT['ru'].keys() if CHAMPIONATS_DICT['ua'][user.champ] == CHAMPIONATS_DICT['ru'][champ]][0])
        users_controller.set_team(user.id, data[user.team])


def update_notifications(user, notification_type):
    if notification_type == 'match_started':
        users_controller.set_notifications(user.id, not user.match_started, user.text_broadcast)
    else:
        users_controller.set_notifications(user.id, user.match_started, not user.text_broadcast)


def handle_monitorings(bot):
    users = users_controller.get_users_with_match_started_enabled()
    while True:
        if datetime.now().minute % 5 == 1:
            for user in users:
                days, hours, minutes = parse.parse_time(user)
                if days == 0:
                    if datetime.now().hour == 10 and not user.match_started_notifs['day_left']:
                        bot.send_message(user.id, LANG_DICT[user.language]['match_today_msg'])
                        bot.send_message(user.id, get_match_info(user),
                                         parse_mode='markdown')
                        users_controller.update_match_started_notifs(user, 'day_left')
                    elif hours == 0 and minutes == 10 and not user.match_started_notifs['ten_minutes_left']:
                        bot.send_message(user.id, LANG_DICT[user.language]['ten_minutes_left_msg'])
                        users_controller.update_match_started_notifs(user, 'ten_minutes_left')
