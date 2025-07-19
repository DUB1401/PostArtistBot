from Source.Core.Functions import AccessAlert, SendPostWithImage, SendPostWithVideo
from Source.Core.Kling import KlingAdapter, KlingOptions
from Source.Core.ImageGenerator import ImageGenerator
from Source.UI import InlineKeyboards
from Source.Core.Queue import Queue

from dublib.Methods.Filesystem import MakeRootDirectories, RemoveDirectoryContent
from dublib.TelebotUtils import TeleCache, TeleMaster, UsersManager
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from time import sleep
import os

from telebot import types
import telebot

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

Clear()
CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(("Data/Buffer", "Data/Users", "Temp"))

Settings = ReadJSON("Settings.json")

if Settings["proxy"]:
	os.environ["HTTP_PROXY"] = Settings["proxy"]
	os.environ["HTTPS_PROXY"] = Settings["proxy"]

Bot = telebot.TeleBot(Settings["bot_token"])
Master = TeleMaster(Bot)

UsersManagerObject = UsersManager("Data/Users")
Cacher = TeleCache()
Cacher.set_bot(Bot)

GeneratorSDXL = ImageGenerator(Settings["sdxl_flash"])
Kling = KlingAdapter(Settings["kling_ai"]["cookies"])
QueueObject = Queue(Bot, GeneratorSDXL, Kling)

MIN_COINS = Settings["kling_ai"]["min_coins"]

#==========================================================================================#
# >>>>> ВЗАИМОДЕЙСТВИЕ С ПОЛЬЗОВАТЕЛЕМ <<<<< #
#==========================================================================================#

@Bot.message_handler(commands = ["about"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("admin"):
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "<b>PostArtistBot</b> является Open Source проектом под лицензией Apache 2.0 за авторством <a href=\"https://github.com/DUB1401\">@DUB1401</a> и использует модели Stable Diffusion Flash и Kling AI в своей работе для генерации иллюстраций и видео к постам. Исходный код и документация доступны в <a href=\"https://github.com/DUB1401/PostArtistBot\">этом</a> репозитории.",
			parse_mode = "HTML",
			disable_web_page_preview = True
		)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["admins"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)
	
	if User.has_permissions("admin"):
		Admins = UsersManagerObject.get_users(include_permissions = "base_access")

		if len(Admins) > 0:
			for Admin in Admins:
				Keyboard = types.InlineKeyboardMarkup()
				Button = types.InlineKeyboardButton(text = "Удалить", callback_data = f"remove_{Admin.id}")
				Keyboard.add(Button)

				Text = [
					 f"<b>Пользователь:</b> <a href=\"https://t.me/{Admin.username}\">{Admin.username}</a>",
					 f"<b>ID:</b> {Admin.id}"
				]

				if Admin.has_permissions("admin"): Text.append("\n<i>Администратор!</i>")

				Bot.send_message(
					chat_id = Message.chat.id,
					text = "\n".join(Text),
					reply_markup = Keyboard if not Admin.has_permissions("admin") else None,
					parse_mode = "HTML",
					disable_web_page_preview = True
				)
				sleep(0.5)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Нет пользователей с дилегированными правами доступа."
			)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["balance"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("admin"):
		if Kling.is_enabled:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = f"Для Kling AI монет доступно: {Kling.coins_count} 🔥",
				reply_markup = InlineKeyboards.close()
			)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Невозможно получить лимиты. Нет доступа.",
				reply_markup = InlineKeyboards.close()
			)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["clear"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.has_permissions("base_access"):
		User.set_property("post", None)
		if os.path.exists(f"Data/Buffer/{Message.from_user.id}"): RemoveDirectoryContent(f"Data/Buffer/{Message.from_user.id}")
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Данные сессии очищены.",
		)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(commands = ["first", "second", "third", "fourth"])
def Command(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	Indexes = {
		"/first": 0,
		"/second": 1,
		"/third": 2,
		"/fourth": 3
	}
	Index = Indexes[Message.text]

	if User.has_permissions("base_access"):

		if Kling.is_enabled and Kling.coins_count > MIN_COINS:
			Bot.send_message(
				chat_id = User.id,
				text = f"Желаете сгенерировать короткое видео на основе этой иллюстрации при помощи <b>Kling AI</b>?\n\nМонет доступно: {Kling.coins_count} 🔥",
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.kling_answer()
			)
			KlingOptions(User).select_image(Index)

		elif User.get_property("post"):
			SendPostWithImage(Bot, User, f"Data/Buffer/{Message.from_user.id}/{Index}.jpg")

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
		AnimationPath = "Data/start.gif"
		Text = "Я бот для генерации иллюстраций, контекстно совместимых с предоставленным текстом, и создан, чтобы помочь вам вести личный блог или канал. Пришлите мне текст для начала работы."
		
		if os.path.exists(AnimationPath):
			StartAnimation = None

			if not Cacher.has_real_cache(AnimationPath):
				Cacher.set_chat_id(User.id)
				StartAnimation = Cacher.cache_real_file(AnimationPath, types.InputMediaAnimation)
			
			else: 
				StartAnimation = Cacher.get_real_cached_file(AnimationPath, types.InputMediaAnimation)
			
			Bot.send_animation(
				chat_id = Message.chat.id,
				animation = StartAnimation.file_id,
				caption = Text
			)

		else: Bot.send_message(chat_id = Message.chat.id, text = Text)

	else: AccessAlert(Message.chat.id, Bot)

@Bot.message_handler(content_types = ["text"])
def Post(Message: types.Message):
	User = UsersManagerObject.auth(Message.from_user)

	if User.expected_type == "prompt":
		Options = KlingOptions(User)
		Options.drop()
		Options.set_prompt(Message.text)

		Bot.send_message(chat_id = User.id, text = "Описание задано.")
		Bot.send_photo(
			chat_id = User.id,
			photo = types.InputFile(Options.image_path),
			caption = Options.prompt or "Настройте вашу генерацию:",
			reply_markup = InlineKeyboards.kling_options(User)
		)

		User.set_expected_type(None)

	else:
		IsPassword = False

		if Message.text == Settings["password"]:
			User.add_permissions(["base_access"])
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Доступ к функциям бота разрешён."
			)
			IsPassword = True

		if Message.text == Settings["admin_password"]:
			User.add_permissions(["admin", "base_access"])
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Доступ к функциям бота от имени администратора разрешён."
			)
			IsPassword = True

		if not IsPassword and User.has_permissions("base_access"):
			User.set_property("post", Message.text)
			Bot.send_message(
				chat_id = User.id,
				text = "Выберите соотношение сторон иллюстрации.",
				reply_markup = InlineKeyboards.select_ratio()
			)

	if not User.has_permissions("base_access"): AccessAlert(Message.chat.id, Bot)
	
@Bot.callback_query_handler(lambda Call: Call.data.startswith("ratio"))
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	Bot.delete_message(User.id, Call.message.id)

	if User.has_permissions("base_access"):
		User.set_property("ratio", Call.data.split("_")[-1])

		if Kling.is_enabled and Kling.coins_count > MIN_COINS:
			Bot.send_message(
				chat_id = User.id,
				text = "Выберите желаемый способ генерации иллюстраций.",
				reply_markup = InlineKeyboards.image_generators()
			)

		else: QueueObject.append_sdxl(User)

	else: AccessAlert(User.id, Bot)

@Bot.callback_query_handler(lambda Call: Call.data.startswith("image_generator"))
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	Bot.delete_message(User.id, Call.message.id)
	Value = Call.data.split("_")[-1]

	if not User.has_permissions("base_access"): 
		AccessAlert(User.id, Bot)
		return
	
	if Value == "kling": QueueObject.append_kling(User)
	else: QueueObject.append_sdxl(User)

@Bot.callback_query_handler(lambda Call: Call.data == "delete_message")
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	TeleMaster(Bot).safely_delete_messages(User.id, Call.message.id)

@Bot.callback_query_handler(lambda Call: Call.data == "kling_yes")
def CallbackQuery_KlingYes(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	Master.safely_delete_messages(User.id, Call.message.id)

	if not User.has_permissions("base_access"): 
		AccessAlert(User.id, Bot)
		return
	
	Options = KlingOptions(User)
	
	Bot.send_photo(
		chat_id = User.id,
		photo = types.InputFile(Options.image_path),
		caption = Options.prompt or "Настройте вашу генерацию:",
		reply_markup = InlineKeyboards.kling_options(User)
	)

@Bot.callback_query_handler(lambda Call: Call.data == "kling_no")
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	Bot.delete_message(User.id, Call.message.id)

	if not User.has_permissions("base_access"): 
		AccessAlert(User.id, Bot)
		return
	
	SendPostWithImage(Bot, User, KlingOptions(User).image_path)
	User.set_property("post", None)
	RemoveDirectoryContent(f"Data/Buffer/{User.id}")

@Bot.callback_query_handler(lambda Call: Call.data.startswith("kling_options_duration"))
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)

	Value: bool = Call.data.split("_")[-1] == "10"
	KlingOptions(User).set_extend(Value)
	
	Bot.edit_message_reply_markup(
		chat_id = User.id,
		message_id = Call.message.id,
		reply_markup = InlineKeyboards.kling_options(User)
	)

@Bot.callback_query_handler(lambda Call: Call.data.startswith("kling_options_prompt"))
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	User.set_expected_type("prompt")
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	Bot.send_message(User.id, "Отправьте описание запроса:")

@Bot.callback_query_handler(lambda Call: Call.data.startswith("kling_options_version"))
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)

	Value: str = Call.data.split("_")[-1]
	Value = "1." + Value[-1]
	KlingOptions(User).select_model(Value)
	
	Bot.edit_message_reply_markup(
		chat_id = User.id,
		message_id = Call.message.id,
		reply_markup = InlineKeyboards.kling_options(User)
	)

@Bot.callback_query_handler(lambda Call: Call.data == "kling_generate")
def CallbackQuery_KlingGenerate(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)
	Master.safely_delete_messages(User.id, Call.message.id)

	if not User.has_permissions("base_access"): 
		AccessAlert(User.id, Bot)
		return
	
	Options = KlingOptions(User)
	User.set_property("last_provider", "kling")
	User.set_property("last_operation", "video")

	Notification = Bot.send_message(User.id, "<i>Видео генерируется. Это займёт от 2 до 5 минут...</i>", parse_mode = "HTML")

	Link = Kling.generate_video(
		image_path = Options.image_path,
		prompt = Options.prompt,
		extend = Options.extend,
		model = Options.model
	)

	Master.safely_delete_messages(User.id, Notification.id)
	SendPostWithVideo(Bot, User, Link)

	Bot.send_message(
		chat_id = User.id,
		text = "Вам понравился результат?",
		reply_markup = InlineKeyboards.retry()
	)

@Bot.callback_query_handler(lambda Call: Call.data == "retry")
def CallbackQuery(Call: types.CallbackQuery):
	User = UsersManagerObject.auth(Call.from_user)

	if not User.has_permissions("base_access"):
		AccessAlert(User.id, Bot)
		return
	
	LastOperation = User.get_property("last_operation")
	Master.safely_delete_messages(User.id, Call.message.id)

	if LastOperation == "images":
		LastProvider = User.get_property("last_provider")

		if LastProvider == "sdxl": QueueObject.append_sdxl(User)
		elif LastProvider == "kling": QueueObject.append_kling(User)

	elif LastOperation == "video": CallbackQuery_KlingYes(Call)

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