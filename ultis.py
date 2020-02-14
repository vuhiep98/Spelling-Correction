import pandas as pd
import re

def remove_diacritics(text):
	diacritic_characters = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúý'+\
			'ĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặ'+\
			'ẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớ'+\
			'ỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
	non_diacritic_characters = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuy'+\
			'AaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAa'+\
			'AaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOo'+\
			'OoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'

	result = ''
	for c in text:
		if c in diacritic_characters:
			result += non_diacritic_characters[
				diacritic_characters.index(c)]
		else:
			result += c
	return result

# def evaluate(test, target):
#     if len(test) != len(target):
#         raise Exception('Not same length')
#     for (t, tg) in zip*([test, target]):
#         for w in t.split()

def memo(f):
	cache = {}
	def fmemo(*arg):
		if arg not in cache:
			cache[arg] = f(*arg)
		return cache[arg]
	fmemo.cache = cache
	return fmemo

def product(lst):
	result = 1
	for x in lst:
		result = result*x
	return result

UNIKEY_TYPO_ERRORS = {"aa": "â", "aw": "ă", "dd": "đ", "ee": "ê", "oo": "ô", "ow": "ơ", "uw": "ư"}

def unikey_typos_handler(text):
	for error in UNIKEY_TYPO_ERRORS:
		text = re.sub(error, UNIKEY_TYPO_ERRORS[error], text)
	return text

NUMBER = "#"

def encode_numbers(text):
	numbers = re.findall(r"\d+", text)
	for num in numbers:
		text = re.sub(num, NUMBER, text)
	return text, numbers

def decode_numbers(text, numbers):
	new_text = ""
	cnt = 0
	for c in text:
		if c == NUMBER:
			new_text += numbers[cnt]
			cnt += 1
		else:
			new_text += c
	return new_text

ALPHABET = "abcdefghijklmnopqrstuvwxyzâăđêôơưàáảãạằắẳẵặấầẩẫậềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ"

def edit(text):
	if len(text) > 20:
		return [text]
	else:
		inserts = [text[:i] + c + text[i:] for i in range(len(text)) for c in ALPHABET]
		deletes = [text[:i] + text[i+1:] for i in range(len(text)-1) for c in ALPHABET]
		replaces = [text[:i] + c + text[i+1:] for i in range(len(text)-1) for c in ALPHABET]
		return list(set(inserts + deletes + replaces))

def edits(text, score=1):
	candidates = edit(text)
	for i in range(1, score):
		new_candidates = []
		for c in candidates:
			new_candidates = list(set(new_candidates + edit(c)))
		candidates = list(set(candidates + new_candidates))
	return candidates
