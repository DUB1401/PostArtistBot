from deep_translator import GoogleTranslator
from gradio_client import Client
from PIL import Image

import shutil
import g4f
import os
import re

#==========================================================================================#
# >>>>> ИСКЛЮЧЕНИЯ <<<<< #
#==========================================================================================#

class BadStepsCount(Exception):

	def __init__(self):
		# Добавление данных в сообщение об ошибке.
		self.__Message = "Use only 1, 2, 4 or 8 steps."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message)
			
	def __str__(self):
		return self.__Message

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ImageGenerator:

	def __CheckUserFolder(self, user_id: int | str):
		# Если папки не существует, создать её.
		if not os.path.exists(f"Data/{user_id}"): os.makedirs(f"Data/{user_id}")

	def __Translate(self, text: str) -> str:
		# Перевод текста.
		text = GoogleTranslator(source = "auto", target = "en").translate(text)
		
		return text

	def __init__(self, settings: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Клиент генератора.
		self.__Client = Client(settings["hf-space"], hf_token = settings["hf-token"])
		self.__Client.output_dir = "./Temp"
		# Список доступных количеств шагов.
		self.__Steps = [1, 2, 4, 8]
		# Глобальные настройки.
		self.__Settings = settings.copy()

	def describe_post_by_gpt(self, post: str) -> str:
		# Текст запроса.
		Request = f"Представь, что ты художник, и кратко опиши иллюстрацию, которую бы ты нарисовал к этому тексту: \"{post}\"."

		try:
			# Выполнение запроса.
			post = g4f.ChatCompletion.create(model = g4f.models.mixtral_8x22b, provider = g4f.Provider.DeepInfra, messages = [{"role": "user", "content": Request}])
			# Удаление упоминания иллюстрации.
			post = re.sub("(И|и)ллюстраци(я|и)", "", post)
			# Удаление исключения.
			post = post.split("<")[0]

		except Exception as ExceptionData:
			# Вывод в консоль: исключение.
			print(ExceptionData)

		return post

	def generate_image_by_gradio(self, user_id: int | str, text: str, filename: str, steps: int = 1) -> bool:
		# Состояние: успешна ли генерация. 
		IsSuccess = False
		# Индекс попытки.
		Try = 0

		# Пока генерация не будет успешной или не закночатся попытки.
		while not IsSuccess and Try < 3:

			try:
				# Если неверное количество шагов, выбросить исключение.
				if steps not in self.__Steps: raise BadStepsCount
				# Проверка существования папки пользователя.
				self.__CheckUserFolder(user_id)
				# Перевод и уточнение запроса.
				text = " ".join(self.__Settings["parameters"]) + " " + self.__Translate(text)
				# Запрос к нейросети.
				Result = self.__Client.predict(text.strip(), f"{steps}-Step", api_name = "/generate_image")
				# Перемещение файла в директорию скрипта с новым именем.
				shutil.move(Result, f"./Data/{user_id}/{filename}.jpg")
				# Чтение изображения.
				CurrentImage = Image.open(f"./Data/{user_id}/{filename}.jpg")
				# Список цветов изображения.
				ColorsList = CurrentImage.getcolors()
				# Если в изображении используется более одного цвета, считать генерацию успешной.
				if ColorsList == None or len(CurrentImage.getcolors()) > 1: IsSuccess = True
			
			except Exception as ExceptionData: print(ExceptionData)

			# Инкремент попытки.
			Try += 1

		return IsSuccess