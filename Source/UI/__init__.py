from telebot import types

class InlineKeyboards:
	"""Набор Inline-клавиатур."""

	def select_ration() -> types.InlineKeyboardMarkup:
		"""Генерирует Inline-клавиатуру: выбор соотношения."""

		Menu = types.InlineKeyboardMarkup()
		Horizontal = types.InlineKeyboardButton("16:9", callback_data = "ratio_horizontal")
		Square = types.InlineKeyboardButton("1:1", callback_data = "ratio_square")
		Vertical = types.InlineKeyboardButton("9:16", callback_data = "ratio_vertical")
		Menu.add(Horizontal, Square, Vertical, row_width = 3)

		return Menu