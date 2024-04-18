from dublib.Methods import CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON, RemoveFolderContent
from Source.ImageGenerator import ImageGenerator
from Source.Functions import GenerateImagesList
from Source.Users import UsersManager
from telebot import types

import telebot

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Data/Users", "Temp"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Чтение настроек.
Settings = ReadJSON("Settings.json")
# Если токен не указан, выбросить исключение.
if type(Settings["token"]) != str or Settings["token"].strip() == "": raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> ВЗАИМОДЕЙСТВИЕ С ПОЛЬЗОВАТЕЛЕМ <<<<< #
#==========================================================================================#

# Токен для работы определенного бота телегамм.
Bot = telebot.TeleBot(Settings["token"])
# Инициализация интерфейсов.
UsersManagerObject = UsersManager()
ImageGeneratorObject = ImageGenerator(Settings)
# Словарь общения с подмодулями.
ComData = {
	"users-manager": UsersManagerObject,
	"image-generator": ImageGeneratorObject,
	"bot": Bot,
	"settings": Settings
}

# Обработка команды: start.
@Bot.message_handler(commands = ["start"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message.from_user)
	# Отправка сообщения: приветствие.
	Bot.send_message(
		chat_id = Message.chat.id,
		text = "Я бот для генерации иллюстраций, контекстно совместимых с предоставленным текстом и создан, чтобы помочь вам вести личный блог или канал. Пришлите мне пост для начала работы."
	)

# Обработка команд: first, second, thirt, fourth.
@Bot.message_handler(commands = ["first", "second", "third", "fourth"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message.from_user)

	# Если у пользователя есть пост.
	if User.post:
		# Индексы команд.
		Indexes = {
			"/first": 0,
			"/second": 1,
			"/third": 2,
			"/fourth": 3
		}
		# Определение индекса.
		Index = Indexes[Message.text]
		# Загрузка иллюстрации.
		Media = [
			types.InputMediaPhoto(
				open(f"Data/{Message.from_user.id}/{Index}.jpg", "rb"), 
				caption = User.post,
				parse_mode = "HTML"
			)
		]

		try:
			# Отправка сообщения: предпросмотр.
			Bot.send_media_group(
				chat_id = Message.chat.id,
				media = Media
			)

		except:
			# Реинициализация подписи.
			Media = [
				types.InputMediaPhoto(
					open(f"Data/{Message.from_user.id}/{Index}.jpg", "rb"),
					caption = "*Не удалось прикрепить иллюстрацию к посту, так как он имеет недопустимую длину!*",
					parse_mode = "MarkdownV2"
				)
			]
			# Отправка сообщения: иллюстрация.
			Bot.send_media_group(
				chat_id = Message.chat.id,
				media = Media
			)
			# Отправка сообщения: пост.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = User.post,
				parse_mode = "HTML"
			)

		# Удаление текста поста.
		UsersManagerObject.set_user_value(Message.from_user.id, "post", None)
		# Удаление файлов.
		RemoveFolderContent(f"Data/{Message.from_user.id}")

	else:
		# Отправка сообщения: не задан текст поста.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Вы не отправили текст поста для генерации иллюстрации.",
		)

# Обработка команды: retry.
@Bot.message_handler(commands = ["retry"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message.from_user)

	# Если пост сохранён.
	if User.post:
		# Генерация иллюстраций.
		GenerateImagesList(ComData, Message, User)

	else:
		# Отправка сообщения: не задан текст поста.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Вы не отправили текст поста для генерации иллюстрации.",
		)

# Обработка команды: clear.
@Bot.message_handler(commands = ["clear"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message.from_user)
	# Удаление текста поста.
	UsersManagerObject.set_user_value(Message.from_user.id, "post", None)
	# Удаление файлов.
	RemoveFolderContent(f"Data/{Message.from_user.id}")
	# Отправка сообщения: данные сессии очищены.
	Bot.send_message(
		chat_id = Message.chat.id,
		text = "Данные сессии очищены.",
	)

# Обработка текстовых сообщений.
@Bot.message_handler(content_types = ["text"])
def Post(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message.from_user)
	# Запоминание текста поста.
	UsersManagerObject.set_user_value(Message.from_user.id, "post", Message.html_text)
	# Генерация иллюстраций.
	GenerateImagesList(ComData, Message, User)
	
# Запуск обработки запросов Telegram.
Bot.infinity_polling()