from Source.Core.ImageGenerator import ImageGenerator

from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.TelebotUtils import UserData

from threading import Thread
from time import sleep

from telebot import TeleBot, types

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Queue:
	"""Очередь генерации иллюстраций."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __QueueProcessor(self):
		"""Обрабатывает очередь запросов."""

		while True:

			if len(self.__QueueData):
				User: UserData = self.__QueueData[0]
				Index = 0
				Message = None
				
				try:
					Message = self.__Bot.send_message(
						chat_id = User.id,
						text = "Инициализация выделенного ядра нейросети..."
					)
					
					while Index < 4:
						RequestText = User.get_property("post")
						Message = self.__Bot.edit_message_text(
							chat_id = User.id,
							message_id = Message.message_id,
							text = "Идёт генерация иллюстраций...\n\nПрогресс: " + str(Index + 1) + " / 4"
						)
						
						Result = self.__ImageGenerator.generate_image_by_gradio(User, RequestText, str(Index))

						if Result:
							Media = [
								types.InputMediaPhoto(
									open(f"Data/Buffer/{User.id}/{Index}.jpg", "rb"), 
									caption = f"Используйте команду /" + self.__ImagesSelectors[Index] + " для выбора данной иллюстрации.",
								)
							]
							self.__Bot.edit_message_text(
								chat_id = User.id,
								message_id = Message.message_id,
								text = "Идёт генерация иллюстраций...\n\nПрогресс: " + str(Index + 1) + " / 4 (отправка)",
							)
							self.__Bot.send_media_group(User.id, media = Media)
							Index += 1

							if Index == 4: 
								self.__QueueData.pop(0)
								self.__Bot.send_message(
									chat_id = Message.chat.id,
									text = "Если вам не понравился ни один из предложенных вариантов, воспользуйтесь командой /retry для генерации ещё четырёх иллюстраций."
								)

						else:
							self.__Bot.send_message(
								chat_id = User.id,
								text = "<i>Достигнут лимит запросов. Попробуйте продолжить позже.</i>",
								parse_mode = "HTML"
							)
							self.__QueueData.pop(0)
							
				except Exception as ExceptionData: print(ExceptionData)

				self.__Bot.delete_message(User.id, Message.message_id)
				RemoveDirectoryContent("Temp")

			else: break

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict, bot: TeleBot):
		"""
		Оператор очереди генерации иллюстраций.

		:param settings: Словарь глобальных настроек.
		:type settings: dict
		:param bot: Бот Telegram.
		:type bot: TeleBot
		"""

		self.__Settings = settings.copy()
		self.__Bot = bot

		self.__QueueData = list()
		self.__ImageGenerator = ImageGenerator(self.__Settings)
		self.__ProcessorThread = None
		self.__ImagesSelectors = ("first", "second", "third", "fourth")
		
		self.run()

	def append(self, user: UserData):
		"""
		Добавляет пользователя в очередь для генерации иллюстраций.

		:param user: Данные пользователя.
		:type user: UserData
		"""
		
		IsFirst = not bool(len(self.__QueueData))
		self.__QueueData.append(user)
		self.run()

		if not IsFirst: self.__Bot.send_message(
			chat_id = user.id,
			text = "В данный момент кто-то уже генерирует иллюстрацию. Ваш запрос помещён в очередь и будет обработан сразу же, как появится возможность."
		)

	def run(self):
		"""Запускает поток обработки очереди запросов."""

		if self.__ProcessorThread == None or not self.__ProcessorThread.is_alive():
			self.__ProcessorThread = Thread(target = self.__QueueProcessor)
			self.__ProcessorThread.start()