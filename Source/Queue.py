from Source.ImageGenerator import ImageGenerator

from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.TelebotUtils import UserData
from telebot import TeleBot, types
from huggingface_hub import HfApi
from threading import Thread
from time import sleep

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Request:
	"""Данные запроса на генерацию."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def chat_id(self) -> int:
		"""Идентификатор чата."""

		return self.__ChatID

	@property
	def user(self) -> int:
		"""Объектное представление пользователя."""

		return self.__User

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, chat_id: int, user: UserData):

		#---> Генерация динамических свойств.
		#==========================================================================================
		self.__ChatID = chat_id
		self.__User = user

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
				CurrentRequest = self.__QueueData[0]
				Index = 0
				Message = None
				
				try:
					Message = self.__Bot.send_message(
						chat_id = CurrentRequest.chat_id,
						text = "Инициализация выделенного ядра нейросети\\.\\.\\.",
						parse_mode = "MarkdownV2"
					)
					
					while Index < 4:
						RequestText = CurrentRequest.user.get_property("post")

						if self.__Settings["describe-by-gpt"]:
							Description = CurrentRequest.user.get_property("description")

							if not Description:
								self.__Bot.edit_message_text(
									chat_id = CurrentRequest.chat_id,
									message_id = Message.message_id,
									text = "Выполняется описание запроса при помощи модели GPT-4\\.\\.\\.",
									parse_mode = "MarkdownV2"
								)
								Description = self.__ImageGenerator.describe_post_by_gpt(RequestText)
								CurrentRequest.user.create_property("description", Description)

							RequestText = Description
						
						Message = self.__Bot.edit_message_text(
							chat_id = CurrentRequest.chat_id,
							message_id = Message.message_id,
							text = "Идёт генерация иллюстраций\\.\\.\\.\n\nПрогресс: " + str(Index + 1) + " / 4",
							parse_mode = "MarkdownV2"
						)
						Result = self.__ImageGenerator.generate_image_by_gradio(CurrentRequest.user.id, RequestText, Index, steps = self.__Settings["steps"])

						if Result:
							Media = [
								types.InputMediaPhoto(
									open(f"Data/{CurrentRequest.user.id}/{Index}.jpg", "rb"), 
									caption = f"Используйте команду /" + self.__ImagesSelectors[Index] + " для выбора данной иллюстрации.",
								)
							]
							self.__Bot.edit_message_text(
								chat_id = CurrentRequest.chat_id,
								message_id = Message.message_id,
								text = "Идёт генерация иллюстраций\\.\\.\\.\n\nПрогресс: " + str(Index + 1) + " / 4 \\(отправка\\)",
								parse_mode = "MarkdownV2"
							)
							self.__Bot.send_media_group(CurrentRequest.chat_id, media = Media)
							Index += 1

						else:
							self.__Bot.edit_message_text(
								chat_id = CurrentRequest.chat_id,
								message_id = Message.message_id,
								text = "Идёт генерация иллюстраций\\.\\.\\.\n\nПрогресс: " + str(Index + 1) + " / 4\n\n_Достигнут лимит запросов\\. Подождите несколько минут для получения следующей иллюстрации\\._",
								parse_mode = "MarkdownV2"
							)
							sleep(30)

				except Exception as ExceptionData: print(ExceptionData)

				self.__Bot.delete_message(CurrentRequest.chat_id, Message.message_id)
				self.__Bot.send_message(
					chat_id = Message.chat.id,
					text = "Если вам не понравился ни один из предложенных вариантов, воспользуйтесь командой /retry для генерации ещё четырёх иллюстраций."
				)
				self.__QueueData.pop(0)
				RemoveDirectoryContent("Temp")
				if self.__Settings["hf-token"]: self.__HuggingAPI.restart_space(self.__Settings["hf-space"], token = self.__Settings["hf-token"])

			else: break

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict, bot: TeleBot, autorun: bool = True):
		"""
		Очередь генерации иллюстраций.
			settings – глобальные настройки;
			bot – ссылка на объект бота.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================
		self.__Settings = settings.copy()
		self.__Bot = bot
		self.__HuggingAPI = HfApi(token = self.__Settings["hf-token"])
		self.__QueueData = list()
		self.__ImageGenerator = ImageGenerator(self.__Settings)
		self.__ProcessorThread = None
		self.__ImagesSelectors = ["first", "second", "third", "fourth"]
		
		if autorun: self.run()

	def append(self, chat_id: int, user: UserData):
		"""
		Добавляет пользователя в очередь для генерации иллюстраций.
			chat_id – идентификатор чата;
			user – объектное представление данных пользователя.
		"""

		IsFirst = not bool(len(self.__QueueData))
		self.__QueueData.append(Request(chat_id, user))
		self.run()

		if not IsFirst: self.__Bot.send_message(
			chat_id = chat_id,
			text = "В данный момент кто-то уже генерирует иллюстрацию. Ваш запрос помещён в очередь и будет обработан сразу же, как появится возможность."
		)

	def run(self):
		"""Запускает поток обработки очереди запросов."""

		if self.__ProcessorThread == None or not self.__ProcessorThread.is_alive():
			self.__ProcessorThread = Thread(target = self.__QueueProcessor, name = "Queue processor.")
			self.__ProcessorThread.start()