from dublib.TelebotUtils import UserData
from telebot import types
from time import sleep

import telebot 

def AccessAlert(ChatID: int, Bot: telebot.TeleBot):
	# Отправка сообщения: не хватает прав.
	Bot.send_message(
		chat_id = ChatID,
		text = "У вас не хватает парв для использования данного функционала. Свяжитесь с администратором для получения полномочий."
	)

def GenerateImagesList(ComData: dict, Message: types.Message, User: UserData):
	# Отправка сообщения: ожидание.
	Dump = ComData["bot"].send_message(
		chat_id = Message.chat.id,
		text = "Идёт генерация иллюстраций..."
	)
	# Список команд для выбора иллюстраций.
	ImagesCommands = [
		"first",
		"second",
		"third",
		"fourth"
	]

	try:
		# Для указанного количества попыток.
		for Index in range(4):
			# Текст запроса.
			Request = User.get_property("post")

			# Если используется трансляция через GPT.
			if ComData["settings"]["describe-by-gpt"]:
				# Получение описания поста.
				Description = User.get_property("description")

				# Если пост не имеет описания.
				if not Description or not ComData["settings"]["one-description"]:
					# Генерация описания поста.
					Description = ComData["image-generator"].describe_post_by_gpt(Request)
					# Обновление описания поста.
					ComData["users-manager"].get_user(Message.from_user.id).set("description", Description)

				# Установка описания в качестве текста запроса.
				Request = Description

			# Редактирование сообщения: прогресс.
			ComData["bot"].edit_message_text(
				chat_id = Message.chat.id,
				message_id = Dump.message_id,
				text = "Идёт генерация иллюстраций...\n\nПрогресс: " + str(Index + 1) + " / 4"
			)
			# Генерация изображения.
			Result = ComData["image-generator"].generate_image_by_gradio(Message.from_user.id, Request, Index, steps = ComData["settings"]["steps"])

			# Если генерация успешна.
			if Result:
				# Загрузка иллюстрации.
				Media = [
					types.InputMediaPhoto(
						open(f"Data/{Message.from_user.id}/{Index}.jpg", "rb"), 
						caption = f"Используйте команду /" + ImagesCommands[Index] + " для выбора данной иллюстрации.",
					)
				]
				# Редактирование сообщения: прогресс.
				ComData["bot"].edit_message_text(
					chat_id = Message.chat.id,
					message_id = Dump.message_id,
					text = "Идёт генерация иллюстраций...\n\nПрогресс: " + str(Index + 1) + " / 4 (отправка)"
				)
				# Отправка сообщения: иллюстрация.
				ComData["bot"].send_media_group(Message.chat.id, media = Media)

	except Exception as ExceptionData: print(ExceptionData)

	# Удаление сообщения о генерации.
	ComData["bot"].delete_message(Message.chat.id, Dump.message_id)
	# Отправка сообщения: повторная попытка.
	ComData["bot"].send_message(
		chat_id = Message.chat.id,
		text = "Если вам не понравился ни один из предложенных вариантов, воспользуйтесь командой /retry для генерации ещё четырёх иллюстраций."
	)