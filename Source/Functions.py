import telebot 

def AccessAlert(chat_id: int, bot: telebot.TeleBot):
	bot.send_message(
		chat_id = chat_id,
		text = "У вас не хватает парв для использования данного функционала. Свяжитесь с администратором для получения полномочий."
	)