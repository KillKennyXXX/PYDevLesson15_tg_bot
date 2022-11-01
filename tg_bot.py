import telebot
from telebot import types
import habr_news as habr
import hh_query as hh
from random import sample
import time
import os

name_bot = '@avsTGBot'
TOKEN = '5634294706:AAFsLZ_rnust5eWZgUE60tcMHNa-SbPPYLY'
bot = telebot.TeleBot(TOKEN)

urls = habr.get_news()
news = habr.read_news(urls)
num_news = {}
hh_keys = hh.read_keys_in_db()




@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Здравствуй " + message.from_user.username + " !")

@bot.message_handler(commands=['hh'])
def hh_query(message):
    key = message.text.replace('/hh', '').replace(' ', '')
    if key:
        hh_urls = hh.getUrls(search=key)
        hh_urls = hh_urls['urls']
        url = sample(hh_urls, 1)
        vacancy = hh.read_url(url[0])
        result = ''
        for key, val in vacancy.items():
            if key != 'key_skills' and key != 'info':
                result += f'{key}: {val} \n'

    bot.send_message(message.from_user.id, result)



@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "AVS бот поддерживает следующий набор комманд:\n"
                                           "/start - Приветствие пользователя\n"
                                           "/news - Новости Habr\n"
                                           "/skills - Топ скилы по предложенным ключам с HH\n"
                                           "/hh ключ- Поиск вакансий по ключу с HH (ключ - обязательный параметр)\n"
                                           "/help - Дополнительная информация ")


@bot.message_handler(commands=['news'])
def habr_news(message):
    global news
    global num_news
    num = message.text.replace('/news', '').replace(' ', '')
    if num:
        try:
            num = int(num)

        except:
            num = 100  # Такого количества новостей на странице не существует
        if len(news) - num > 0 and num:
            num_news[message.from_user.username] = num - 1
        else:
            num_news[message.from_user.username] = 0
    else:
        try:
            num_news[message.from_user.username] += 1 if len(news) - num_news[message.from_user.username] > 0 else 0
        except:
            num_news[message.from_user.username] = 0

    new = news[num_news[message.from_user.username]]
    if new['title']: bot.send_message(message.from_user.id, new['title'])
    if new['img']: bot.send_message(message.from_user.id, new['img'])
    if new['text']: bot.send_message(message.from_user.id, new['text'])
    num_news[message.from_user.username] += 1 if len(news) - num_news[message.from_user.username] > 0 else 0


@bot.message_handler(commands=['skills'])
def hh_skills(message):
    global hh_keys
    skill = message.text.replace('/skills', '').replace(' ', '')
    if skill in hh_keys:
        bot.send_message(message.from_user.id, hh.read_top_skills_in_db_str(skill))
    else:
        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        for i in range(0, len(hh_keys)):
            key = types.InlineKeyboardButton(text=hh_keys[i], callback_data=hh_keys[i])
            keyboard.add(key)
        bot.send_message(message.from_user.id, text='Обработаны запросы по ключам:\n', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    bot.send_message(call.message.chat.id,  hh.read_top_skills_in_db_str(call.data))
    bot.answer_callback_query(call.id)




bot.polling(none_stop=True, interval=0)

# name = ''
# surname = ''
# age = 0
# def get_age(message):
#     global age
#     while age == 0:  # проверяем что возраст изменился
#         try:
#             age = int(message.text)  # проверяем, что возраст введен корректно
#         except Exception:
#             bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
#     keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
#     key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
#     keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
#     key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
#     keyboard.add(key_no)
#     question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?'
#     bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
#
#
# def get_surname(message):
#     global surname
#     surname = message.text
#     bot.send_message('Сколько тебе лет?')
#     bot.register_next_step_handler(message, get_age)
#
#
# def get_name(message):  # получаем фамилию
#     global name
#     name = message.text
#     bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
#     bot.register_next_step_handler(message, get_surname)


# @bot.callback_query_handler(func=lambda call: True)
# def callback_worker(call):
#     if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
#         # код сохранения данных, или их обработки
#         bot.send_message(call.message.chat.id, 'Запомню : )')
#     elif call.data == "no":
#         pass
        # переспрашиваем

# @bot.message_handler(content_types=['text'])
# def start(message):
#     if message.text == '/start':
#         help(message)
#     else:
#         bot.send_message(message.from_user.id, 'Напиши /start')

# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#     bot.reply_to(message, "Howdy, how are you doing?")
#
#
# # Обработка команд
# @bot.message_handler(commands=['timer'])
# def timer(message):
#     for i in range(5):
#         time.sleep(1)
#         bot.send_message(message.chat.id, i + 1)
#
#
# # Команда в параметром
# @bot.message_handler(commands=['say'])
# def say(message):
#     # получить то что после команды
#     text = ' '.join(message.text.split(' ')[1:])
#     bot.reply_to(message, f'***{text.upper()}!***')
#
#
# # Команда администратора
# @bot.message_handler(commands=['admin'], func=lambda message: message.from_user.username == 'DanteOnline')
# def admin(message):
#     print(message)
#     info = os.name
#     bot.reply_to(message, info)
#
#
# @bot.message_handler(commands=['admin2'])
# def admin2(message):
#     if message.from_user.username == 'DanteOnline':
#         info = os.name
#         bot.reply_to(message, info)
#     else:
#         bot.reply_to(message, 'Метод недоступен, нет прав')
#
#
# @bot.message_handler(commands=['restart'])
# def restart_server(message):
#     # выполнить команду операционки из python
#     # os.system('notepad')
#     bot.reply_to(message, 'ура!')
#
#
# @bot.message_handler(commands=['file'])
# def get_file(message):
#     print('зашел')
#     # Передать какой то файл который есть на диске
#     # with open('text.txt', 'r', encoding='utf-8') as data:
#     #     bot.send_document(message.chat.id, data)
#     with open('pict.jpg', 'rb') as data:
#         bot.send_photo(message.chat.id, data)
#
#
# @bot.message_handler(content_types=['text'])
# def reverse_text(message):
#     if 'плохой' in message.text.lower():
#         bot.reply_to(message, 'В тексте слово плохой')
#         return
#     text = message.text[::-1]
#     bot.reply_to(message, text)
#
#
# @bot.message_handler(content_types=['sticker'])
# def send_sticker(message):
#     FILE_ID = 'CAADAgADPQMAAsSraAsqUO_V6idDdBYE'
#     bot.send_sticker(message.chat.id, FILE_ID)
