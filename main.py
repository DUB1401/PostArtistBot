from dublib.Methods import CheckPythonMinimalVersion, ChunkList, MakeRootDirectories, ReadJSON, RemoveFolderContent
from Source.Functions import AccessAlert, GenerateImagesList
from dublib.TelebotUtils import UsersManager, UserData
from Source.ImageGenerator import ImageGenerator
from dublib.Polyglot import Markdown
from telebot import types
from time import sleep

import telebot
import os

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
UsersManagerObject = UsersManager("Data/Users")
ImageGeneratorObject = ImageGenerator(Settings)
# Словарь общения с подмодулями.
ComData = {
	"users-manager": UsersManagerObject,
	"image-generator": ImageGeneratorObject,
	"bot": Bot,
	"settings": Settings
}

# Обработка команды: about.
@Bot.message_handler(commands = ["about"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет права администратора.
	if User.is_admin:
		# Отправка сообщения: информация о боте.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "*PostArtistBot* является Open Source проектом под лицензией Apache 2\\.0 за авторством [@DUB1401](https://github.com/DUB1401) и использует модели GPT\\-4 и Stable Diffusion XL в своей работе для генерации иллюстраций к постам\\. Исходный код и документация доступны в [этом](https://github.com/DUB1401/PostArtistBot) репозитории\\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: admins.
@Bot.message_handler(commands = ["admins"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)
	
	# Если пользователь имеет права администратора.
	if User.is_admin:
		# Список администраторов.
		Admins = UsersManagerObject.admins
		# Разбить список администраторов на списки по 10 элементов.
		Admins = ChunkList(Admins, 10)

		# Для каждой группы.
		for Group in Admins:
			# Текст сообщения.
			Text = ""

			# Для каждого администратора.
			for Admin in Group:
				# Ник пользователя.
				Username = Markdown(str(Admin.username)).escaped_text
				# Создание описания.
				Text += f"*Пользователь:* [{Username}](https://t.me/{Username})\n*ID:* {Admin.id}\n\n"

			# Отправка сообщения: информация об администраторах.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = Text,
				parse_mode = "MarkdownV2",
				disable_web_page_preview = True
			)
			# Выжидание интервала.
			sleep(1)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: clear.
@Bot.message_handler(commands = ["clear"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет права администратора.
	if User.is_admin:
		# Удаление текста поста.
		User.set("post", None)
		# Удаление файлов.
		if os.path.exists(f"Data/{Message.from_user.id}"): RemoveFolderContent(f"Data/{Message.from_user.id}")
		# Отправка сообщения: данные сессии очищены.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Данные сессии очищены.",
		)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команд: first, second, thirt, fourth.
@Bot.message_handler(commands = ["first", "second", "third", "fourth"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет права администратора.
	if User.is_admin:

		# Если у пользователя есть пост.
		if User.get("post"):
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
					caption = User.get("post"),
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
					text = User.get("post"),
					parse_mode = "HTML"
				)

			# Удаление текста поста.
			User.set("post", None)
			# Удаление файлов.
			RemoveFolderContent(f"Data/{Message.from_user.id}")

		else:
			# Отправка сообщения: не задан текст поста.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не отправили текст поста для генерации иллюстрации.",
			)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: retry.
@Bot.message_handler(commands = ["retry"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет права администратора.
	if User.is_admin:

		# Если пост сохранён.
		if User.get("post"):
			# Генерация иллюстраций.
			GenerateImagesList(ComData, Message, User)

		else:
			# Отправка сообщения: не задан текст поста.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не отправили текст поста для генерации иллюстрации.",
			)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: start.
@Bot.message_handler(commands = ["start"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)
	# Создание свойств пользователя.
	User.set("post", None)
	User.set("description", None)

	# Если пользователь имеет права администратора.
	if User.is_admin:
		# Отправка сообщения: приветствие.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = Settings["start-message"]
		)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка текстовых сообщений.
@Bot.message_handler(content_types = ["text"])
def Post(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если сообщение соответствует паролю.
	if Message.text == Settings["password"]:
		# Выдача прав администратора.
		User.set_admin(True)
		# Отправка сообщения: доступ разрешён.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Доступ к функциям бота разрешён."
		)

	# Если пользователь имеет права администратора.
	elif User.is_admin:
		# Запоминание текста поста.
		User.set("post", Message.html_text)
		# Генерация иллюстраций.
		GenerateImagesList(ComData, Message, User)

	else: AccessAlert(Message.chat.id, Bot)
	
# Запуск обработки запросов Telegram.
Bot.infinity_polling()