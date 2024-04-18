from Source.Users import UserData
from telebot import types
from time import sleep

import telebot 

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
			Request = User.post

			# Если используется трансляция через GPT.
			if ComData["settings"]["describe-by-gpt"]:
				# Получение описания поста.
				Description = User.description

				# Если пост не имеет описания.
				if not User.description or not ComData["settings"]["one-description"]:
					# Генерация описания поста.
					Description = ComData["image-generator"].describe_post_by_gpt(User.post)
					# Обновление описания поста.
					ComData["users-manager"].set_user_value(Message.from_user.id, "description", Description)

				# Установка описания в качестве текста запроса.
				Request = Description

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
				# Отправка сообщения: иллюстрация.
				ComData["bot"].send_media_group(Message.chat.id, media = Media)

	except Exception as ExceptionData: print(ExceptionData)

	# Отправка сообщения: повторная попытка.
	ComData["bot"].send_message(
		chat_id = Message.chat.id,
		text = "Если вам не понравился ни один из предложенных вариантов, воспользуйтесь командой /retry для генерации ещё четырёх иллюстраций."
	)
	# Удаление сообщения о генерации.
	ComData["bot"].delete_message(Message.chat.id, Dump.message_id)