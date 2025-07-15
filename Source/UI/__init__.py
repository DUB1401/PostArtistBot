from Source.Core.Kling import KlingOptions

from dublib.TelebotUtils.Users import UserData

from telebot import types

class InlineKeyboards:
	"""Набор Inline-клавиатур."""

	def image_generators() -> types.InlineKeyboardMarkup:
		"""Генерирует Inline-клавиатуру: выбор генератора иллюстраций."""

		Menu = types.InlineKeyboardMarkup()
		SDXL = types.InlineKeyboardButton("SDXL", callback_data = "image_generator_sdxl")
		Kling = types.InlineKeyboardButton("Kling AI", callback_data = "image_generator_kling")
		Menu.add(SDXL, Kling, row_width = 2)

		return Menu

	def select_ratio() -> types.InlineKeyboardMarkup:
		"""Генерирует Inline-клавиатуру: выбор соотношения."""

		Menu = types.InlineKeyboardMarkup()
		Horizontal = types.InlineKeyboardButton("16:9", callback_data = "ratio_horizontal")
		Square = types.InlineKeyboardButton("1:1", callback_data = "ratio_square")
		Vertical = types.InlineKeyboardButton("9:16", callback_data = "ratio_vertical")
		Menu.add(Horizontal, Square, Vertical, row_width = 3)

		return Menu
	
	def kling_answer() -> types.InlineKeyboardMarkup:
		"""Генерирует Inline-клавиатуру: использование Kling."""

		Menu = types.InlineKeyboardMarkup()
		Yes = types.InlineKeyboardButton("Да", callback_data = "kling_yes")
		No = types.InlineKeyboardButton("Нет", callback_data = "kling_no")
		Menu.add(Yes, No, row_width = 2)

		return Menu
	
	def kling_options(user: UserData) -> types.InlineKeyboardMarkup:
		"""Генерирует Inline-клавиатуру: использование Kling."""

		Options = KlingOptions(user)

		DurationStatus = ("", "✅ ") if Options.extend else ("✅ ", "")
		ModelVersion = ("", "✅ ") if Options.model == "1.6" else ("✅ ", "")

		Menu = types.InlineKeyboardMarkup()
		Prompt = types.InlineKeyboardButton("📝 Задать описание", callback_data = "kling_options_prompt")
		Menu.add(Prompt, row_width = 1)
		FiveSeconds = types.InlineKeyboardButton(DurationStatus[0] + "5 сек.", callback_data = "kling_options_duration_5")
		TenSeconds = types.InlineKeyboardButton(DurationStatus[1] + "10 сек.", callback_data = "kling_options_duration_10")
		Menu.add(FiveSeconds, TenSeconds, row_width = 2)
		OldVersion = types.InlineKeyboardButton(ModelVersion[0] + "v1.0", callback_data = "kling_options_version_10")
		MidleVersion = types.InlineKeyboardButton(ModelVersion[1] + "v1.6", callback_data = "kling_options_version_16")
		Menu.add(OldVersion, MidleVersion, row_width = 2)
		Generate = types.InlineKeyboardButton("🤖 Сгенерировать", callback_data = "kling_generate")
		Menu.add(Generate, row_width = 1)

		return Menu
	
	def close() -> types.InlineKeyboardMarkup:
		"""Генерирует Inline-клавиатуру: удаление сообщения."""

		Menu = types.InlineKeyboardMarkup()
		Close = types.InlineKeyboardButton("Закрыть", callback_data = "delete_message")
		Menu.add(Close)

		return Menu