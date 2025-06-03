from telebot import TeleBot

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