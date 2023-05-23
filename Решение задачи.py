from pprint import pprint
import requests
from tqdm import tqdm
import json

# Класс для работы с API ВК
class VkUser :
    url = 'https://api.vk.com/method/'
    def __init__(self,token,version):
        self.params = {
            'access_token': token,
            'v': version
        }

    # Работаем с фотографиями . Запрос на photos.get :

    def get_photos (self,user_id=None,count=5):
        '''Функция возвращает список
        фотографий в альбоме.
        На вход подаётся id пользователя user_id (по умолчанию id пользователя ,
        производящего запрос ) и количество загружаемых фотографий count
         ( по умолчанию = 5 ).
        На выходе получаем список  словарей  с  информацией о фотографиях - имя , ссылка , размер'''
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id ,
            'album_id': 'wall',
            'rev': 1 ,
            'extended': 1 ,
            'photo_sizes': 1,
            'count': count
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        #pprint(res)
        # Разбираемся с размерами . Вытягиваем в отдельный файл блок "items"
        fotos_items_list = res [ "response"]["items"]
        size_dict = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
        name_photos_list = []
        data_photos_list = []
        for data in fotos_items_list :
            size_max=0
            # добавляем прогресс-бар tqdm :
            for element in tqdm(data['sizes']):
                letter_size_foto = element['type']
                # Проверка на наличии обозначения размера фото в контрольном словаре разиеров:
                if letter_size_foto in size_dict.keys():
                  # Ищем фото с максимальным размером , сохраняем соответствующую букву размера (letter_max_foto)
                    # и ссылку на фото максимального размера (url_foto)
                    if size_dict[letter_size_foto] > size_max:
                        size_max = size_dict[letter_size_foto]
                        url_foto = element['url']
                        letter_max_foto = letter_size_foto

                else:
                     print(f'Ошибка. Размера "{letter_size_foto}" нет в контрольном списке размеров фотографий')
             # Определяемся с именем выбранной фотографии
            # Задаём имя , равное количеству лайков для данной фотографии
            name_foto = data['likes']['count']
            # Проверяем на равенство лайков под разными фото
            if name_foto in name_photos_list :
               # Если количество лайков совпадает, к  имени добавим дату загрузки фото
               name_foto = f"{name_foto}_{data['date']}"
               name_photos_list.append(name_foto)
            else:
               name_photos_list.append(name_foto)
            # Сохраняем данные о выбранном фото в текущем словаре:
            element_dict={
            'name_foto':f'{name_foto}.jpg',
            'url_foto':url_foto,
           'type_size_photo':letter_max_foto
            }
            # Добавляем текущий словарь в общий список из словарей с данными о выбранных фото:
            data_photos_list.append(element_dict)
        return data_photos_list

# Класс для загрузки на Яндекс - диск

class YandexDisk:

    def __init__(self, token):
        self.token = token

    # Функция получения заголовков
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }



    # Функция , загружающая файл на Яндекс-диск методом POST :
    def post_upload_file (self,disk_file_path, url_photo):
        '''Функция загрузки файла  на Яндекс Диск
        методом POST . На вход получает путь к месту загрузки файла
        с именем файла (disk_file_path) и url загружаемого файла (url_photo)'''
        headers = self.get_headers()
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload/"
        params = {"path": disk_file_path, "url":url_photo  , "overwrite": True}
        response = requests.post(url=upload_url, params=params, headers=headers)
        response.raise_for_status()
        if response.status_code == 202:
            print("Файл успешно загружен")







# Работаем с ВК:
token = ''
# Инициализируем объект класса VkUser :
vk_client = VkUser(token, '5.131')

# Запускаем на просчёт функцию get_photos().
# На выходе получаем список словарей с данными о фото , которые сохраняем в переменную fotos_data
fotos_data = vk_client.get_photos(count=7)
#pprint (fotos_data)
# [{'name_foto': '7.jpg',
#   'type_size_photo': 'w',
#   'url_foto': 'https://sun9-6.userapi.com/impg/eXTivWQStkMnuQ9ukGmznzCF5jlVzD6klO9SMA/pc37y6AR1lk.jpg?size=1200x1800&quality=95&sign=7b77ad705b89f5d996ed1fe341389bd0&c_uniq_tag=wHjFMO8fSo0OGDXOymwd_JmK4Tt1R3wylZaAWi29LmE&type=album'},

# Приступаем к работе с Яндекс Диском .
TOKEN = ''
# Инициализируем объект класса YandexDisk :
ya = YandexDisk(token=TOKEN)

# Создаём список словарей с данными о загружаемых файлах
final_data_list = []

# Загружаем серию фото по данным из fotos_data, добавляем прогресс-бар tqdm :
for photo in tqdm(fotos_data) :

    # Создадим текущий словарь с данными о загруженных фотографиях:
    final_data_dict = {
    'file_name':photo['name_foto'],
    'size':photo['type_size_photo']
    }
    final_data_list.append(final_data_dict)

    url_photo = photo.get('url_foto')
    name_photo = photo.get('name_foto')

    # Загружаем на Яндекс-диск в папку "netology"
    ya.post_upload_file(f'netology/{name_photo}',url_photo )

# Сохраним выходные данные в json - файл final_json :
with open('final_json.json','w') as f :
    json.dump(final_data_list, f, ensure_ascii=False, indent=2)



