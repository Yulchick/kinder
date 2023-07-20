from pprint import pprint
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import db

from operator import itemgetter

from config import comunity_token, acces_token

vk_c = vk_api.VkApi(token=comunity_token)
vk_a = vk_api.VkApi(token=acces_token)
longpoll = VkLongPoll(vk_c)

data_user_for_find = {}
'''словарь с данными для поиска id , sity, sex'''


def write_msg(user_id, message, attachment=None):
    vk_c.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                  "attachment": attachment})


def session_longpoll():
    """получаем ответ в чате бота"""
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            write_msg(user_id, f"Идет поиск, {event.user_id}")
            request_user = event.text.lower()

            return request_user, user_id


def start():
    """начало"""
    requests_longpoll, user_id = session_longpoll()
    print('-----', requests_longpoll, user_id)
    if requests_longpoll == 'q':
        print('q')
        get_profile_user(user_id)


def change_sex(data_user_ff, user_id):
    if data_user_ff['sex'] == 1:
        data_user_for_find['sex'] = 2
        find_users(data_user_for_find, user_id)
    else:
        data_user_for_find['sex'] = 1
        find_users(data_user_for_find, user_id)


def find_users(user_for_find, user_id):
    n = user_for_find['bdate'].split('.')
    resp = vk_a.method('users.search', {
        'age_to': int(n[2]) + 3,
        'sex': user_for_find['sex'],
        'city': user_for_find['city'],
        'fields': 'bdate,sex,photo_id,about,city,relation,inerests,domain',
        'status': 6,
        'count': 25,
        'has_photo': 1,
        'v': 5.131
    })
    pprint(resp)
    creating_a_list(resp['items'], user_id)


def creating_a_list(resp, user_id):
    result = []

    for i in resp:
        r = []
        if not i['is_closed']:
            r.append(i['id'])
            r.append(i['first_name'])
            r.append(i['last_name'])

            result.append(r)

    get_foto_likes_list(result, user_id)


def get_user_foto(i):
    """Принимает список айди  возвращает список списков [ количество лайков,самых популярных id] """
    global url
    list_foto = []
    session = vk_api.VkApi(token=acces_token)
    response = session.method('photos.get', {
        'owner_id': i,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1})
    a = response['items']

    for item in a:
        list_foto.append(item['likes']['count'])
        url = item['sizes'][0]['url']

    return list_foto, url


def get_foto_likes_list(list_foto, user_id):
    """получаем список с ай ди, имя,фамилия и получаем лайки с фото"""
    for items in list_foto:
        lists, url = get_user_foto(items[0])
        items.append(sum(lists))
        items.append(url)
    sorted_list(list_foto, user_id)


def sorted_list(list_foto, user_id):
    list_foto = (sorted(list_foto, key=itemgetter(3), reverse=True))
    create_presentation(list_foto, user_id)


def create_presentation(list_foto, user_id):
    print('great  list', list_foto)
    list_presentation = []
    for i in list_foto:
        res = db.send_db(i[0])
        if res is None:
            list_presentation.append(i)
            if len(list_presentation) == 3:
                presentation(list_presentation, user_id, list_foto)

        else:
            print('есть в базе', i)


def presentation(list_foto, user_id, l_f_p):
    print('llllllllll', list_foto, l_f_p)
    for item in list_foto:
        print('item', item)
        write_msg(user_id, f'{item[1]},{item[2]}', attachment=item[4])
        db.save_tabel_data_user(item[0], item[4])
        what_to_do(l_f_p, user_id)


def what_to_do(l_f_p, user_id):
    print('what to do', l_f_p)
    write_msg(user_id, 'Что будем делать далее ( d - смотреть далее / любая другая кнопка - начинаем новый поиск)',
              attachment=None)
    resp, user_id = session_longpoll()
    if resp == 'd':
        create_presentation(l_f_p, user_id)
    else:
        start()


def get_profile_user(user_id):
    """получаем информацию о пользователе и заносим в словарь, возвращаем словарь"""

    req = vk_a.method('users.get', {'user_id': user_id, 'fields': 'bdate,city,sex,photo_id,about'})
    data_user_for_find['bdate'] = req[0]['bdate']
    data_user_for_find['city'] = req[0]['city']['id']
    data_user_for_find['sex'] = req[0]['sex']
    print('data for find', data_user_for_find)
    change_sex(data_user_for_find, user_id)


db.drop_table()
db.create_table()

start()
