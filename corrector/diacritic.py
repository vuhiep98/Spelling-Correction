from dictionary import Dictionary

class DiacriticAdder(Dictionary):
	def __init__(self):
		pass

	def add_diacritic(self, text):
		tokens = text.split()