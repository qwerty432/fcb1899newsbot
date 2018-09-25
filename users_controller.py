from db import connect
from sqlalchemy import Table, Column, Integer, String, Boolean, ARRAY, JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select
import json

con, meta = connect()

def create_user_table():
    try:
        users = Table('users', meta,
                      Column('id', Integer, primary_key=True),
                      Column('username', String),
                      Column('language', String(2)),
                      Column('champ', String(20)),
                      Column('state', String(50)),
                      Column('team', String(20)),
                      Column('match_started', Boolean),
                      Column('text_broadcast', Boolean),
                      Column('match_started_notifs', JSON),
                      Column('news_urls', ARRAY(String), default=[])
                     )
        meta.create_all(con)
    except:
        print('Table already exists')


def delete_all_users():
    try:
        user_table = meta.tables['users']
        con.execute(user_table.delete())
    except KeyError:
        print('Table does not exist')


def drop_user_table():
    try:
        user_table = meta.tables['users']
        user_table.drop()
    except KeyError:
        print('Table does not exist')


def create_user(message):
    users = meta.tables['users']
    query = users.insert().values(id=message.chat.id,
                                   username=message.from_user.username,
                                   state='start',
                                   language='ua',
                                   match_started=False,
                                   text_broadcast=False,
                                   match_started_notifs={'day_left': False, 'ten_minutes_left': False, 'started': False})
    try:
        con.execute(query)
    except IntegrityError:
        print('User with id {} already exists'.format(message['id']))


def get_all_users():
    try:
        users = meta.tables['users']
    except KeyError:
        print('Table does not exist')
    query = select([users])
    result = con.execute(query)

    for row in result:
        print(row)


def get_users_with_match_started_enabled():
    try:
        users = meta.tables['users']
    except KeyError:
        print('Table does not exist')
    query = select([users]).where(users.c.match_started == True)
    result = con.execute(query)

    try:
        result = con.execute(query).fetchall()
        print(result)
    except:
        print('Error with getting users')

    return result


def get_user(user_id):
    users = meta.tables['users']
    query = users.select().where(users.c.id == user_id)

    try:
        result = con.execute(query).fetchone()
    except:
        print('Table does not exist')

    return result


def update_state(user_id, state):
    users = meta.tables['users']
    query = users.update().where(users.c.id == user_id).values(state=state)

    con.execute(query)


def set_urls(user_id, urls):
    users = meta.tables['users']
    query = users.update().where(users.c.id == user_id).values(news_urls=urls)

    con.execute(query)


def set_team(user_id, team_name):
    users = meta.tables['users']
    query = users.update().where(users.c.id == user_id).values(team=team_name)

    con.execute(query)


def set_champ(user_id, champ):
    users = meta.tables['users']
    query = users.update().where(users.c.id == user_id).values(champ=champ)

    con.execute(query)


def set_lang(user_id, lang):
    if lang == 'ru':
        change_lang = 'ua'
    else:
        change_lang = 'ru'

    users = meta.tables['users']
    query = users.update().where(users.c.id == user_id).values(language=change_lang)

    con.execute(query)


def set_notifications(user_id, match_started, text_broadcast):
    users = meta.tables['users']
    query = users.update().where(users.c.id == user_id).values(match_started=match_started,
                                                               text_broadcast=text_broadcast)

    con.execute(query)


def update_match_started_notifs(user, key=None):
    notification_dict = user.match_started_notifs
    if key is not None:
        notification_dict[key] = not notification_dict[key]
    for notif_key in notification_dict:
        if notif_key != key:
            notification_dict[notif_key] = False

    users = meta.tables['users']
    query = users.update().where(users.c.id == user.id).values(match_started_notifs=notification_dict)

    con.execute(query)
