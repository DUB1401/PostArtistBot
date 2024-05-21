from Source.ImageGenerator import ImageGenerator
from dublib.Methods import RemoveFolderContent
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
		#==========================================================================================#
		# ID чата.
		self.__ChatID = chat_id
		# Объектное представление пользователя.
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

		# Постоянно.
		while True:

			# Если в очереди есть запрос.
			if len(self.__QueueData):
				# Текущий запрос.
				CurrentRequest = self.__QueueData[0]
				# Индекс повтора.
				Index = 0
				# Данные об общении с пользователем.
				Message = None
				
				try:
					# Редактирование сообщения: выделение ядра.
					Message = self.__Bot.send_message(
						chat_id = CurrentRequest.chat_id,
						text = "Инициализация выделенного ядра нейросети\\.\\.\\.",
						parse_mode = "MarkdownV2"
					)
					
					# Четыре раза.
					while Index < 4:
						# Текст запроса.
						RequestText = CurrentRequest.user.get_property("post")

						# Если используется трансляция через GPT.
						if self.__Settings["describe-by-gpt"]:
							# Получение описания поста.
							Description = CurrentRequest.user.get_property("description")

							# Если пост не имеет описания.
							if not Description:
								# Редактирование сообщения: описание поста при помощи GPT.
								self.__Bot.edit_message_text(
									chat_id = CurrentRequest.chat_id,
									message_id = Message.message_id,
									text = "Выполняется описание запроса при помощи модели GPT-4\\.\\.\\.",
									parse_mode = "MarkdownV2"
								)
								# Генерация описания поста.
								Description = self.__ImageGenerator.describe_post_by_gpt(RequestText)
								# Обновление описания поста.
								CurrentRequest.user.create_property("description", Description)

							# Установка описания в качестве текста запроса.
							RequestText = Description
						
						# Редактирование сообщения: прогресс.
						Message = self.__Bot.edit_message_text(
							chat_id = CurrentRequest.chat_id,
							message_id = Message.message_id,
							text = "Идёт генерация иллюстраций\\.\\.\\.\n\nПрогресс: " + str(Index + 1) + " / 4",
							parse_mode = "MarkdownV2"
						)
						# Генерация изображения.
						Result = self.__ImageGenerator.generate_image_by_gradio(CurrentRequest.user.id, RequestText, Index, steps = self.__Settings["steps"])

						# Если генерация успешна.
						if Result:
							# Загрузка иллюстрации.
							Media = [
								types.InputMediaPhoto(
									open(f"Data/{CurrentRequest.user.id}/{Index}.jpg", "rb"), 
									caption = f"Используйте команду /" + self.__ImagesSelectors[Index] + " для выбора данной иллюстрации.",
								)
							]
							# Редактирование сообщения: прогресс (отправка).
							self.__Bot.edit_message_text(
								chat_id = CurrentRequest.chat_id,
								message_id = Message.message_id,
								text = "Идёт генерация иллюстраций\\.\\.\\.\n\nПрогресс: " + str(Index + 1) + " / 4 \\(отправка\\)",
								parse_mode = "MarkdownV2"
							)
							# Отправка сообщения: иллюстрация.
							self.__Bot.send_media_group(CurrentRequest.chat_id, media = Media)
							# Инкремент индекса.
							Index += 1

						else:
							# Редактирование сообщения: требуется подождать.
							self.__Bot.edit_message_text(
								chat_id = CurrentRequest.chat_id,
								message_id = Message.message_id,
								text = "Идёт генерация иллюстраций\\.\\.\\.\n\nПрогресс: " + str(Index + 1) + " / 4\n\n_Достигнут лимит запросов\\. Подождите несколько минут для получения следующей иллюстрации\\._",
								parse_mode = "MarkdownV2"
							)
							# Выжидание интервала.
							sleep(30)

				except Exception as ExceptionData: print(ExceptionData)

				# Удаление сообщения о генерации.
				self.__Bot.delete_message(CurrentRequest.chat_id, Message.message_id)
				# Отправка сообщения: повторная попытка.
				self.__Bot.send_message(
					chat_id = Message.chat.id,
					text = "Если вам не понравился ни один из предложенных вариантов, воспользуйтесь командой /retry для генерации ещё четырёх иллюстраций."
				)
				# Удаление запроса из очереди.
				self.__QueueData.pop(0)
				# Удаление временных файлов.
				RemoveFolderContent("Temp")
				# Перезапуск пространсва.
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
		#==========================================================================================#
		# Глобальные настройки.
		self.__Settings = settings.copy()
		# Ссылка на объект бота.
		self.__Bot = bot
		# Обработчик API Hugging Face.
		self.__HuggingAPI = HfApi(token = self.__Settings["hf-token"])
		# Очередь запросов.
		self.__QueueData = list()
		# Генератор иллюстраций.
		self.__ImageGenerator = ImageGenerator(self.__Settings)
		# Поток обработки запросов.
		self.__ProcessorThread = None
		# Список команд для выбора иллюстраций.
		self.__ImagesSelectors = ["first", "second", "third", "fourth"]

		# Если указано, запустить поток обработки.
		if autorun: self.run()

	def append(self, chat_id: int, user: UserData):
		"""
		Добавляет пользователя в очередь для генерации иллюстраций.
			chat_id – идентификатор чата;
			user – объектное представление данных пользователя.
		"""

		# Состояние: первым ли в очереди пользователь.
		IsFirst = not bool(len(self.__QueueData))
		# Добавление запроса в очередь.
		self.__QueueData.append(Request(chat_id, user))
		# Запуск потока обработки.
		self.run()
		# Отправка сообщения: пользователь не первый в очереди.
		if not IsFirst: self.__Bot.send_message(
			chat_id = chat_id,
			text = "В данный момент кто-то уже генерирует иллюстрацию. Ваш запрос помещён в очередь и будет обработан сразу же, как появится возможность."
		)

	def run(self):
		"""Запускает поток обработки очереди запросов."""

		# Если поток не функционирует, запустить его.
		if self.__ProcessorThread == None or not self.__ProcessorThread.is_alive():
			# Реинициализация и запуск потока.
			self.__ProcessorThread = Thread(target = self.__QueueProcessor, name = "Queue processor.")
			self.__ProcessorThread.start()