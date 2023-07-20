import sqlalchemy
# from sqlalchemy.orm import declarative_base
# from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

import psycopg2

c = 1

'''адрес бд'''
DSN = 'postgresql://postgres:qwr1d@localhost:5432/postgres'

'''создаем движок'''
engine = sqlalchemy.create_engine(DSN)

connect = psycopg2.connect(database='postgres', user='postgres', password='qwr1d')

Session = sessionmaker(bind=engine)


def drop_table():
    with connect.cursor() as cursor:
        cursor.execute('''
                            drop table data_user;

                        ''')
    connect.commit()
    print('удалена таблица data_user')


def create_table():
    with connect.cursor() as cursor:
        cursor.execute('''
                create table if not exists data_user(
                    id serial primary key,
                    id_user int,
                    foto_url varchar(250) unique

                    );
            ''')
        connect.commit()
        print('создана таблица data_user')


def save_tabel_data_user(id_u, url):
    with connect.cursor() as cursor:
        cursor.execute('''
                                      insert into data_user(id_user,foto_url)
                                      values(%s,%s); 

                                  ''', (id_u, url))
        connect.commit()
        print('данные внесены')


def send_db(id_u):
    a = str(id_u)
    with connect.cursor() as cur:
        cur.execute('''
                select id from data_user where id_user = %s;
            ''', (a,))
        a = cur.fetchone()

        return a
