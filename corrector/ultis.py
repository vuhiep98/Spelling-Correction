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

NUMBER = "<num>"

def encode_numbers(text):
	numbers = re.findall(r"[\S]*\d+[\S]*", text)
	for num in numbers:
		text = text.replace(num, NUMBER, 1)
	return text, numbers

def decode_numbers(text, numbers):
	new_text = []
	cnt = 0
	for c in text.split():
		if c == NUMBER:
			new_text += [numbers[cnt]]
			cnt += 1
		else:
			new_text += [c]
	return " ".join(new_text)

ALPHABET = "abcdefghijklmnopqrstuvwxyzâăđêôơưàáảãạằắẳẵặấầẩẫậềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ"

def edit(word):
	if len(word) > 20:
		return [word]
	else:
		inserts = [word[:i] + c + word[i:] for i in range(len(word)) for c in ALPHABET]
		deletes = [word[:i] + word[i+1:] for i in range(len(word)) for c in ALPHABET]
		replaces = [word[:i] + c + word[i+1:] for i in range(len(word)) for c in ALPHABET]
		
		return list(set([word] + inserts + deletes + replaces))

def edits(text, score=1):
	candidates = edit(text)
	for i in range(1, score):
		new_candidates = []
		for c in candidates:
			new_candidates = list(set(new_candidates + edit(c)))
		candidates = list(set(candidates + new_candidates))
	return candidates

