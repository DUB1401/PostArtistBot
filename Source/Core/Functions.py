from dublib.TelebotUtils.Users import UserData

from telebot import TeleBot, types
from os import PathLike

def AccessAlert(chat_id: int, bot: TeleBot):
	"""
	Отправляет пользователю уведомление о недостаточных правах.

	:param chat_id: ID чата.
	:type chat_id: int
	:param bot: Бот Telegram.
	:type bot: TeleBot
	"""

	bot.send_message(
		chat_id = chat_id,
		text = "У вас не хватает парв для использования данного функционала. Свяжитесь с администратором для получения полномочий."
	)

def SendPostWithImage(bot: TeleBot, user: UserData, image_path: PathLike):
	"""
	Отправляет пост с иллюстрацией и очищает временный каталог пользователя.

	:param bot: Бот Telegram.
	:type bot: TeleBot
	:param user: Данные пользователя.
	:type user: UserData
	:param image_path: Путь к изображению.
	:type image_path: PathLike
	"""

	try:
		bot.send_photo(
			chat_id = user.id,
			photo = types.InputFile(image_path),
			caption = user.get_property("post"),
			parse_mode = "HTML"
		)

	except Exception as ExceptionData:
		print(ExceptionData)
		bot.send_message(
			chat_id = user.id,
			text = "<i>Не удалось прикрепить иллюстрацию к посту, так как превышен лимит на длину текста.</i>",
			parse_mode = "HTML"
		)
		bot.send_photo(chat_id = user.id, photo = types.InputFile(image_path))
		bot.send_message(chat_id = user.id, text = user.get_property("post"), parse_mode = "HTML")

def SendPostWithVideo(bot: TeleBot, user: UserData, video_url: str):
	"""
	Отправляет пост с иллюстрацией и очищает временный каталог пользователя.

	:param bot: Бот Telegram.
	:type bot: TeleBot
	:param user: Данные пользователя.
	:type user: UserData
	:param video_url: Ссылка на видео.
	:type video_url: str
	"""

	try:
		bot.send_video(
			chat_id = user.id,
			video = video_url,
			caption = user.get_property("post"),
			parse_mode = "HTML"
		)

	except Exception as ExceptionData:
		print(ExceptionData)
		bot.send_message(
			chat_id = user.id,
			text = "<i>Не удалось прикрепить видео к посту, так как превышен лимит на длину текста.</i>",
			parse_mode = "HTML"
		)
		bot.send_video(chat_id = user.id, video = video_url)
		bot.send_message(chat_id = user.id, text = user.get_property("post"), parse_mode = "HTML")