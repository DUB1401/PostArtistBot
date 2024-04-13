from deep_translator import GoogleTranslator
from gradio_client import Client
import shutil
import os

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ ТИПЫ ДАННЫХ <<<<< #
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

	def __init__(self, Settings: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Клиент генератора.
		self.__Client = Client("AP123/SDXL-Lightning")
		# Список доступных количеств шагов.
		self.__Steps = [1, 2, 4, 8]
		# Глобальные настройки.
		self.__Settings = Settings.copy()

	def generate_image_by_gradio(self, user_id: int | str, text: str, filename: str, steps: int = 1) -> bool:
		# Состояние: успешна ли генерация. 
		IsSuccess = True

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
		
		except ValueError:
			# Переключение статуса.
			IsSuccess = False

		return IsSuccess