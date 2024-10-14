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
		
		self.__Message = "Use only 1, 2, 4 or 8 steps."
		super().__init__(self.__Message)
			
	def __str__(self):
		return self.__Message

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ImageGenerator:

	def __CheckUserFolder(self, user_id: int | str):
		if not os.path.exists(f"Data/{user_id}"): os.makedirs(f"Data/{user_id}")

	def __Translate(self, text: str) -> str:
		text = GoogleTranslator(source = "auto", target = "en").translate(text)
		
		return text

	def __init__(self, settings: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================
		self.__Client = Client(settings["hf-space"], hf_token = settings["hf-token"])
		self.__Client.output_dir = "./Temp"
		self.__Steps = [1, 2, 4, 8]
		self.__Settings = settings.copy()

	def describe_post_by_gpt(self, post: str) -> str:
		
		Request = f"Представь, что ты художник, и кратко опиши иллюстрацию, которую бы ты нарисовал к этому тексту: \"{post}\"."

		try:
			post = g4f.ChatCompletion.create(model = g4f.models.gpt_4, provider = g4f.Provider.Bing, messages = [{"role": "user", "content": Request}])
			post = re.sub("(И|и)ллюстраци(я|и)", "", post)
			post = post.split("<")[0]

		except Exception as ExceptionData: print(ExceptionData)

		return post

	def generate_image_by_gradio(self, user_id: int | str, text: str, filename: str, steps: int = 1) -> bool:
		IsSuccess = False
		Try = 0
		text = text.split(" ")[:75]
		text = " ".join(text)
		if steps not in self.__Steps: raise BadStepsCount
		self.__CheckUserFolder(user_id)
		text = ", ".join(self.__Settings["parameters"]) + " \n" + self.__Translate(text)
		
		while not IsSuccess and Try < 3:

			try:
				Result = self.__Client.predict(text.strip(), f"{steps}-Step", api_name = "/generate_image")
				shutil.move(Result, f"./Data/{user_id}/{filename}.jpg")
				CurrentImage = Image.open(f"./Data/{user_id}/{filename}.jpg")
				ColorsList = CurrentImage.getcolors()
				if ColorsList == None or len(CurrentImage.getcolors()) > 1: IsSuccess = True
			
			except Exception as ExceptionData: print(ExceptionData)
			
			Try += 1

		return IsSuccess