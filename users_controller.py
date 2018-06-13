from db import connect
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

con, meta = connect()

def create_user_table():
    try:
        users = Table('users', meta,
            Column('id', Integer, primary_key=True),
            Column('username', String),
            Column('state', String(50))
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


def create_user(message):
    users = meta.tables['users']
    query = users.insert().values(id=message.chat.id,
                                   username=message.from_user.username,
                                   state='start')
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
