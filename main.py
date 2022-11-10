import random
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)

import strings as st
# from settings import API_KEY #создать файл settings.py и вписать туда токен своего бота -> API_KEY = 'токен'

# Включим ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов разговора
GENDER, PHOTO, LOCATION, BIO = range(4)

# функция обратного вызова точки входа в разговор
def start(update, _):
    # Список кнопок для ответа
    reply_keyboard = [['Boy', 'Girl', 'Other']]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # Начинаем разговор с вопроса
    update.message.reply_text(
        'Меня зовут профессор Бот. Я проведу с тобой беседу. '
        'Команда /cancel, чтобы прекратить разговор.\n\n'
        'Ты мальчик или девочка?',
        reply_markup=markup_key,)
    # переходим к этапу `GENDER`, это значит, что ответ
    # отправленного сообщения в виде кнопок будет список 
    # обработчиков, определенных в виде значения ключа `GENDER`
    return GENDER

# Обрабатываем пол пользователя
def gender(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал пол пользователя
    logger.info("Пол %s: %s", user.first_name, update.message.text)
    # Следующее сообщение с удалением клавиатуры `ReplyKeyboardRemove`
    update.message.reply_text(
        'Хорошо. Пришли мне свою фотографию, чтоб я знал как ты '
        'выглядишь, или отправь /skip, если стесняешься.',
        reply_markup=ReplyKeyboardRemove(),
    )
    # переходим к этапу `PHOTO`
    return PHOTO

# Обрабатываем фотографию пользователя
def photo(update, _):
    # определяем пользователя
    user = update.message.from_user
    # захватываем фото 
    photo_file = update.message.photo[-1].get_file()
    # скачиваем фото 
    photo_file.download(f'{user.first_name}_photo.jpg')
    # Пишем в журнал сведения о фото
    logger.info("Фотография %s: %s", user.first_name, f'{user.first_name}_photo.jpg')
    # Отвечаем на сообщение с фото
    update.message.reply_text(
        'Великолепно! А теперь пришли мне свое'
        ' местоположение, или /skip если параноик..'
    )
    # переходим к этапу `LOCATION`
    return LOCATION

# Обрабатываем команду /skip для фото
def skip_photo(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал сведения о фото
    logger.info("Пользователь %s не отправил фото.", user.first_name)
    # Отвечаем на сообщение с пропущенной фотографией
    update.message.reply_text(
        'Держу пари, ты выглядишь великолепно! А теперь пришлите мне'
        ' свое местоположение, или /skip если параноик.'
    )
    # переходим к этапу `LOCATION`
    return LOCATION

# Обрабатываем местоположение пользователя
def location(update, _):
    # определяем пользователя
    user = update.message.from_user
    # захватываем местоположение пользователя
    user_location = update.message.location
    # Пишем в журнал сведения о местоположении
    logger.info(
        "Местоположение %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude)
    # Отвечаем на сообщение с местоположением
    update.message.reply_text(
        'Может быть, я смогу как-нибудь навестить тебя!' 
        ' Расскажи мне что-нибудь о себе...'
    )
    # переходим к этапу `BIO`
    return BIO

# Обрабатываем команду /skip для местоположения
def skip_location(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал сведения о местоположении
    logger.info("User %s did not send a location.", user.first_name)
    # Отвечаем на сообщение с пропущенным местоположением
    update.message.reply_text(
        'Точно параноик! Ну ладно, тогда расскажи мне что-нибудь о себе...'
    )
    # переходим к этапу `BIO`
    return BIO

# Обрабатываем сообщение с рассказом/биографией пользователя
def bio(update, _):
    # Список кнопок для ответа
    reply_keyboard = [['Yes', 'No', 'Other']]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал биографию или рассказ пользователя
    logger.info("Пользователь %s рассказал: %s", user.first_name, update.message.text)
    # Отвечаем на то что пользователь рассказал.
    update.message.reply_text(
        'Спасибо! А теперь, давай, сыграем в крестики-нолики!\n'
        'Команда /play, чтобы начать игру.\n'
        'Команда /cancel, чтобы прекратить разговор.',
    )
    # Предлагаем игру.
     
# проверка на выигрыш
# проверяет нет ли победной комбинации в строчках, столбцах или по диагонали
# arr - массив
# who - кого надо проверить: нужно передать значение 'х' или '0'
def isWin(arr, who):
    if (((arr[0] == who) and (arr[4] == who) and (arr[8] == who)) or
            ((arr[2] == who) and (arr[4] == who) and (arr[6] == who)) or
            ((arr[0] == who) and (arr[1] == who) and (arr[2] == who)) or
            ((arr[3] == who) and (arr[4] == who) and (arr[5] == who)) or
            ((arr[6] == who) and (arr[7] == who) and (arr[8] == who)) or
            ((arr[0] == who) and (arr[3] == who) and (arr[6] == who)) or
            ((arr[1] == who) and (arr[4] == who) and (arr[7] == who)) or
            ((arr[2] == who) and (arr[5] == who) and (arr[8] == who))):
        return True
    return False


# возвращает количество неопределенных ячеек (т.е. количество ячеек, в которые можно сходить)
# cellArray - массив данных из callBackData, полученных после нажатия на callBack-кнопку
def countUndefinedCells(cellArray):
    counter = 0
    for i in cellArray:
        if i == st.SYMBOL_UNDEF:
            counter += 1
    return counter


# callBackData формат:
# n????????? - общее описание
# n - номер кнопки
# ? - один из вариантов значения клетки: смотри модуль strings, раздел "символы, которые используются"
# пример: 5❌❌⭕⭕❌❌◻◻❌
# означает, что была нажата пятая кнопка, и текущий вид поля:
# ❌❌⭕
# ⭕❌❌
# ◻◻❌
# данные обо всем состоянии поля необходимо помещать в кнопку, т.к. бот имеет доступ к информации только из текущего сообщения

# игра: проверка возможности хода крестиком, проверка победы крестика, ход бота (ноликом), проверка победы ботом
# возвращает:
# message - сообщение, которое надо отправить
# callBackData - данные для формирования callBack данных обновленного игрового поля
def game(callBackData):
    # -------------------------------------------------- global message  # использование глобальной переменной message
    message = st.ANSW_YOUR_TURN  # сообщение, которое вернется
    alert = None

    buttonNumber = int(callBackData[0])  # считывание нажатой кнопки, преобразуя ее из строки в число
    if not buttonNumber == 9:  # цифра 9 передается в первый раз в качестве заглушки. Т.е. если передана цифра 9, то клавиатура для сообщения создается впервые
        charList = list(callBackData)  # строчка callBackData разбивается на посимвольный список "123" -> ['1', '2', '3']
        charList.pop(0)  # удаление из списка первого элемента: который отвечает за выбор кнопки
        if charList[buttonNumber] == st.SYMBOL_UNDEF:  # проверка: если в нажатой кнопке не выбран крестик/нолик, то можно туда сходить крестику
            charList[buttonNumber] = st.SYMBOL_X  # эмуляция хода крестика
            if isWin(charList, st.SYMBOL_X):  # проверка: выиграл ли крестик после своего хода
                message = st.ANSW_YOU_WIN
            else:  # если крестик не выиграл, то может сходит бот, т.е. нолик
                if countUndefinedCells(charList) != 0:  # проверка: есть ли свободные ячейки для хода
                    # если есть, то ходит бот (нолик)
                    isCycleContinue = True
                    # запуск бесконечного цикла т.к. необходимо, чтобы бот походил в свободную клетку, а клетка выбирается случайным образом
                    while (isCycleContinue):
                        rand = random.randint(0, 8)  # генерация случайного числа - клетки, в которую сходит бот
                        if charList[rand] == st.SYMBOL_UNDEF:  # если клетка неопределенна, то ходит бот
                            charList[rand] = st.SYMBOL_O
                            isCycleContinue = False  # смена значения переменной для остановки цикла
                            if isWin(charList, st.SYMBOL_O):  # проверка: выиграл ли бот после своего кода
                                message = st.ANSW_BOT_WIN

        # если клетка, в которую хотел походить пользователь уже занята:
        else:
            alert = st.ALERT_CANNOT_MOVE_TO_THIS_CELL

        # проверка: остались ли свободные ячейки для хода и что изначальное сообщение не поменялось (означает, что победителя нет, и что это был не ошибочный ход)
        if countUndefinedCells(charList) == 0 and message == st.ANSW_YOUR_TURN:
            message = st.ANSW_DRAW

        # формирование новой строчки callBackData на основе сделанного хода
        callBackData = ''
        for c in charList:
            callBackData += c

    # проверка, что игра закончилась (message равно одному из трех вариантов: победил Х, 0 или ничья):
    if message == st.ANSW_YOU_WIN or message == st.ANSW_BOT_WIN or message == st.ANSW_DRAW:
        message += '\n'
        for i in range(0, 3):
            message += '\n | '
            for j in range(0, 3):
                message += callBackData[j + i * 3] + ' | '
        callBackData = None  # обнуление callBackData

    return message, callBackData, alert


# Формат объекта клавиатуры
# в этом примере описана клавиатура из трех строчек кнопок
# в первой строчке две кнопки
# во 2-ой и 3-ей строчке по одной
# keyboard = [
#     # строчка из кнопок:
#     [
#         # собственно кнопки
#         InlineKeyboardButton("Кнопка 1", callback_data='1'),
#         InlineKeyboardButton("Кнопка 2", callback_data='2'),
#     ],
#     [InlineKeyboardButton("Кнопка 3", callback_data='3')],
#     [InlineKeyboardButton("Кнопка 4", callback_data='4')],
# ]
# для формирования объекта клавиатуры, необходимо выполнить следующую команду:
# InlineKeyboardMarkup(keyboard)

# возвращает клавиатуру для бота
# на вход получает callBackData - данные с callBack-кнопки
def getKeyboard(callBackData):
    keyboard = [[], [], []]  # заготовка объекта клавиатуры, которая вернется

    if callBackData != None:  # если
        # формирование объекта клавиатуры
        for i in range(0, 3):
            for j in range(0, 3):
                keyboard[i].append(InlineKeyboardButton(callBackData[j + i * 3], callback_data=str(j + i * 3) + callBackData))

    return keyboard


def newGame(update, _):
    # сформировать callBack данные для первой игры, то есть строку, состояющую из 9 неопределенных символов
    data = ''
    for i in range(0, 9):
        data += st.SYMBOL_UNDEF

    # отправить сообщение для начала игры
    update.message.reply_text(st.ANSW_YOUR_TURN, reply_markup=InlineKeyboardMarkup(getKeyboard(data)))


def button(update, _):
    query = update.callback_query
    callbackData = query.data  # получение callbackData, скрытых в кнопке

    message, callbackData, alert = game(callbackData)  # игра
    if alert is None:  # если не получен сигнал тревоги (alert==None), то редактируем сообщение и меняем клавиатуру
        query.answer()  # обязательно нужно что-то отправить в ответ, иначе могут возникнуть проблемы с ботом
        query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(getKeyboard(callbackData)))
    else:  # если получен сигнал тревоги (alert!=None), то отобразить сообщение о тревоге
        query.answer(text=alert, show_alert=True)


def help_command(update, _):
    update.message.reply_text(st.ANSW_HELP)

    return ConversationHandler.END
    # update.message.reply_text('Спасибо! Надеюсь, когда-нибудь снова сможем поговорить.')
    # # Заканчиваем разговор.
    # return ConversationHandler.END

# Обрабатываем команду /cancel если пользователь отменил разговор
def cancel(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал о том, что пользователь не разговорчивый
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    # Отвечаем на отказ поговорить
    update.message.reply_text(
        'Мое дело предложить - твоё отказаться'
        ' Будет скучно - пиши.', 
        reply_markup=ReplyKeyboardRemove()
    )
    # Заканчиваем разговор.
    return ConversationHandler.END

if __name__ == '__main__':
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater("Token")
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler` 
    # с состояниями GENDER, PHOTO, LOCATION BIO
    conv_handler = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('start', start)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчики
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('play', newGame))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, help_command))  # обработчик на любое текстовое сообщение
    updater.dispatcher.add_handler(CallbackQueryHandler(button))  # добавление обработчика на CallBack кнопки

    # Запуск бота
    updater.start_polling()
    updater.idle()