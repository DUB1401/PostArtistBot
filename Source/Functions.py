from Source.ImageGenerator import ImageGenerator
from Source.Users import UserData
from telebot import types

import telebot 

def GenerateImagesList(Settings: dict, Bot: telebot.TeleBot, ImageGeneratorObject: ImageGenerator, Message: types.Message, User: UserData):
	# Отправка сообщения: ожидание.
	Dump = Bot.send_message(
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

	# Для указанного количества попыток.
	for Index in range(4):
		# Генерация изображения.
		Result = ImageGeneratorObject.generate_image_by_gradio(Message.from_user.id, User.post, Index, steps = Settings["steps"])

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
			Bot.send_media_group(Message.chat.id, media = Media)

	# Отправка сообщения: повторная попытка.
	Bot.send_message(
		chat_id = Message.chat.id,
		text = "Если вам не понравился ни один из предложенных вариантов, воспользуйтесь командой /retry для генерации ещё четырёх иллюстраций."
	)
	# Удаление сообщения о генерации.
	Bot.delete_message(Message.chat.id, Dump.message_id)