from Source.Functions import AccessAlert
from Source.Queue import Queue

from dublib.Methods.Filesystem import MakeRootDirectories, RemoveDirectoryContent
from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.TelebotUtils import UsersManager
from dublib.Polyglot import Markdown
from telebot import types
from time import sleep

import telebot
import os

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(["Data/Users", "Temp"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

Settings = ReadJSON("Settings.json")
if type(Settings["bot-token"]) != str or Settings["bot-token"].strip() == "": raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> ВЗАИМОДЕЙСТВИЕ С ПОЛЬЗОВАТЕЛЕМ <<<<< #
#==========================================================================================#

Bot = telebot.TeleBot(Settings["bot-token"])

UsersManagerObject = UsersManager("Data/Users")
QueueObject = Queue(Settings, Bot)

@Bot.message_handler(commands = ["about"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("admin"):
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "*PostArtistBot* является Open Source проектом под лицензией Apache 2\\.0 за авторством [@DUB1401](https://github.com/DUB1401) и использует модели GPT\\-4 и Stable Diffusion XL в своей работе для генерации иллюстраций к постам\\. Исходный код и документация доступны в [этом](https://github.com/DUB1401/PostArtistBot) репозитории\\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["admins"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)
	
	if User.has_permissions("admin"):
		Admins = UsersManagerObject.get_users(include_permissions = "base_access", exclude_permissions = "admin")

		if len(Admins) > 0:
			for Admin in Admins:
				Keyboard = types.InlineKeyboardMarkup()
				Button = types.InlineKeyboardButton(text = "Удалить", callback_data = f"remove_{Admin.id}")
				Keyboard.add(Button)
				Username = Markdown(str(Admin.username)).escaped_text
				Text = f"*Пользователь:* [{Username}](https://t.me/{Username})\n*ID:* {Admin.id}\n\n"
				Bot.send_message(
					chat_id = Message.chat.id,
					text = Text,
					reply_markup = Keyboard,
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True
				)
				sleep(0.5)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Нет пользователей с дилегированными правами доступа."
			)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["clear"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("base_access"):
		User.set_property("post", None)
		if os.path.exists(f"Data/{Message.from_user.id}"): RemoveDirectoryContent(f"Data/{Message.from_user.id}")
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Данные сессии очищены.",
		)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["first", "second", "third", "fourth"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("base_access"):

		if User.get_property("post"):
			Indexes = {
				"/first": 0,
				"/second": 1,
				"/third": 2,
				"/fourth": 3
			}
			Index = Indexes[Message.text]
			Media = [
				types.InputMediaPhoto(
					open(f"Data/{Message.from_user.id}/{Index}.jpg", "rb"), 
					caption = User.get_property("post"),
					parse_mode = "HTML"
				)
			]

			try:
				Bot.send_media_group(
					chat_id = Message.chat.id,
					media = Media
				)

			except:
				Media = [
					types.InputMediaPhoto(
						open(f"Data/{Message.from_user.id}/{Index}.jpg", "rb"),
						caption = "*Не удалось прикрепить иллюстрацию к посту, так как он имеет недопустимую длину!*",
						parse_mode = "MarkdownV2"
					)
				]
				Bot.send_media_group(
					chat_id = Message.chat.id,
					media = Media
				)
				Bot.send_message(
					chat_id = Message.chat.id,
					text = User.get_property("post"),
					parse_mode = "HTML"
				)

			User.set_property("post", None)
			RemoveDirectoryContent(f"Data/{Message.from_user.id}")

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не отправили текст поста для генерации иллюстрации.",
			)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["about"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("admin"):
		Bot.send_message(
			chat_id = Message.chat.id,
			text = Message.text + " отозваны",
			#parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["retry"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("base_access"):

		if User.get_property("post"):
			User.set_property("description", None)
			QueueObject.append(Message.chat.id, User)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не отправили текст поста для генерации иллюстрации.",
			)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["password"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("admin"):

		try:
			Settings["password"] = Message.text.split(" ")[1]
			WriteJSON("Settings.json", Settings)

		except IndexError:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не указали новый пароль. Используйте команду по схеме:\n\n/password [STRING*]",
			)
		
		except:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Во время смены пароля возникла ошибка. Обратитесь к разработчику."
			)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Пароль успешно изменён."
			)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["start"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)
	User.set_property("post", None)
	User.set_property("description", None)

	if User.has_permissions("base_access"):
		Bot.send_message(
			chat_id = Message.chat.id,
			text = Settings["start-message"]
		)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(content_types = ["text"])
def Post(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)
	IsPassword = False

	if Message.text == Settings["password"]:
		User.add_permissions(["base_access"])
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Доступ к функциям бота разрешён."
		)
		IsPassword = True

	if Message.text == Settings["admin-password"]:
		User.add_permissions(["admin", "base_access"])
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Доступ к функциям бота от имени администратора разрешён."
		)
		IsPassword = True

	if not IsPassword and User.has_permissions("base_access"):
		User.set_property("post", Message.html_text)
		QueueObject.append(Message.chat.id, User)

	elif not IsPassword: AccessAlert(Message.chat.id, Bot)
	
@Bot.callback_query_handler(func = lambda Query: True)
def CallbackQuery(Query: types.CallbackQuery):
	User = UsersManagerObject.auth(Query.from_user)
	
	if User.has_permissions("admin"):
		TargetID = Query.data.split("_")[-1]
		TargetUser = UsersManagerObject.get_user(TargetID)
		TargetUser.remove_permissions("base_access")
		Bot.delete_message(Query.message.chat.id, Query.message.message_id)
		Bot.send_message(
			chat_id = Query.message.chat.id,
			text = f"Право доступа к боту отозвано у пользователя с ID {TargetID}.",
		)

Bot.infinity_polling()