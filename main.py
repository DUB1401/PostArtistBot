from dublib.Methods import CheckPythonMinimalVersion, ChunkList, MakeRootDirectories, ReadJSON, RemoveFolderContent, WriteJSON
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
	if User.has_permissions("admin"):
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
	if User.has_permissions("admin"):
		# Список пользователей с доступом к боту.
		Admins = UsersManagerObject.get_users(include_permissions = "base_access", exclude_permissions = "admin")

		# Если пользователи с доступом есть.
		if len(Admins) > 0:
			# Для каждого администратора.
			for Admin in Admins:
				# Создание и настройка Inline-клавиатуры.
				Keyboard = types.InlineKeyboardMarkup()
				Button = types.InlineKeyboardButton(text = "Удалить", callback_data = f"remove_{Admin.id}")
				Keyboard.add(Button)
				# Ник пользователя.
				Username = Markdown(str(Admin.username)).escaped_text
				# Создание описания.
				Text = f"*Пользователь:* [{Username}](https://t.me/{Username})\n*ID:* {Admin.id}\n\n"
				# Отправка сообщения: информация об пользователе.
				Bot.send_message(
					chat_id = Message.chat.id,
					text = Text,
					reply_markup = Keyboard,
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True
				)
				# Выжидание интервала.
				sleep(0.5)

		else:
			# Отправка сообщения: пользователей с доступом нет.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Нет пользователей с дилегированными правами доступа."
			)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: clear.
@Bot.message_handler(commands = ["clear"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет право доступа.
	if User.has_permissions("base_access"):
		# Удаление текста поста.
		User.set_property("post", None)
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

	# Если пользователь имеет право доступа.
	if User.has_permissions("base_access"):

		# Если у пользователя есть пост.
		if User.get_property("post"):
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
					caption = User.get_property("post"),
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
					text = User.get_property("post"),
					parse_mode = "HTML"
				)

			# Удаление текста поста.
			User.set_property("post", None)
			# Удаление файлов.
			RemoveFolderContent(f"Data/{Message.from_user.id}")

		else:
			# Отправка сообщения: не задан текст поста.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не отправили текст поста для генерации иллюстрации.",
			)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: remove.
@Bot.message_handler(commands = ["about"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет права администратора.
	if User.has_permissions("admin"):
		# Отправка сообщения: право доступа отозвано.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = Message.text + " отозваны",
			#parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: password.
@Bot.message_handler(commands = ["password"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)

	# Если пользователь имеет право доступа.
	if User.has_permissions("admin"):

		try:
			# Изменение пароля.
			Settings["password"] = Message.text.split(" ")[1]
			# Сохранение конфигурации.
			WriteJSON("Settings.json", Settings)

		except IndexError:
			# Отправка сообщения: не задан пароль.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не указали новый пароль. Используйте команду по схеме:\n\n/password [STRING*]",
			)
		
		except:
			# Отправка сообщения: не удалось установить пароль.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Во время смены пароля возникла ошибка. Обратитесь к разработчику."
			)

		else:
			# Отправка сообщения: новый пароль доступа установлен.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Пароль успешно изменён."
			)

	else: AccessAlert(Message.chat.id, Bot)

# Обработка команды: start.
@Bot.message_handler(commands = ["start"])
def Command(Message: types.Message):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Message)
	# Создание свойств пользователя.
	User.set_property("post", None)
	User.set_property("description", None)

	# Если пользователь имеет право доступа.
	if User.has_permissions("base_access"):
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
	# Состояние: осуществлялся ли ввод пароля.
	IsPassword = False

	# Если сообщение соответствует паролю.
	if Message.text == Settings["password"]:
		# Выдача прав администратора.
		User.add_permissions(["base_access"])
		# Отправка сообщения: доступ разрешён.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Доступ к функциям бота разрешён."
		)
		# Переключение состояния.
		IsPassword = True

	# Если сообщение соответствует паролю администратора.
	if Message.text == Settings["admin-password"]:
		# Выдача прав администратора.
		User.add_permissions(["admin", "base_access"])
		# Отправка сообщения: доступ разрешён.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Доступ к функциям бота от имени администратора разрешён."
		)
		# Переключение состояния.
		IsPassword = True

	# Если пароль не вводился и пользователь имеет право доступа.
	if not IsPassword and User.has_permissions("base_access"):
		# Запоминание текста поста.
		User.set_property("post", Message.html_text)
		# Генерация иллюстраций.
		GenerateImagesList(ComData, Message, User)

	elif not IsPassword: AccessAlert(Message.chat.id, Bot)
	
# Обработка Inline-запросов: remove.
@Bot.callback_query_handler(func = lambda Query: True)
def CallbackQuery(Query: types.CallbackQuery):
	# Авторизация пользователя.
	User = UsersManagerObject.auth(Query)
	
	# Если пользователь имеет право доступа.
	if User.has_permissions("admin"):
		# ID цели.
		TargetID = Query.data.split("_")[-1]
		# Целевой пользователь.
		TargetUser = UsersManagerObject.get_user(TargetID)
		# Удаление права доступа.
		TargetUser.remove_permissions("base_access")
		# Удаление сообщения: данные пользователя.
		Bot.delete_message(Query.message.chat.id, Query.message.message_id)
		# Отправка сообщения: у пользователя отозваны право доступа.
		Bot.send_message(
			chat_id = Query.message.chat.id,
			text = f"Право доступа к боту отозвано у пользователя с ID {TargetID}.",
		)

# Запуск обработки запросов Telegram.
Bot.infinity_polling()