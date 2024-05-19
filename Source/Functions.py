from time import sleep

import telebot 

def AccessAlert(chat_id: int, bot: telebot.TeleBot):
	# Отправка сообщения: не хватает прав.
	bot.send_message(
		chat_id = chat_id,
		text = "У вас не хватает парв для использования данного функционала. Свяжитесь с администратором для получения полномочий."
	)