from ultis import product
from math import log, log10

# load models
def load_dict(dict_type="uni", diacritic=True):
	dct = {}
	n = 0

	if dict_type == "uni":
		file_name = "unigrams.txt"
	elif dict_type == "bi":
		file_name = "bigrams.txt"
	elif dict_type == "tri":
		file_name = "trigrams.txt"

	model_dir = "model/"

	if diacritic == False:
		model_dir += "non_diacritic_model/"
	
	with open(model_dir + file_name, "r", encoding="utf-8") as reader:
		for line in reader.readlines():
			line = line.replace("\n", "")
			key = line[:line.rindex(" ")]
			value = int(line[line.rindex(" ")+1:])
			dct[key] = value
			n += value
	return dct, n

UNIGRAM, N_UNI = load_dict(dict_type="uni")
BIGRAM, N_BI = load_dict(dict_type="bi")

ND_UNIGRAM, N_ND_UNI = load_dict(dict_type="uni", diacritic=False)
ND_BIGRAM, N_ND_BI = load_dict(dict_type="bi", diacritic=False)

# probability of a word
def pw(word, diacritic=True):
	if diacritic == False:
		try:
			return float(ND_UNIGRAM[word])/N_ND_UNI
		except KeyError:
			return 10./(N_ND_UNI * 10**len(word))
	else:
		try:
			return float(UNIGRAM[word])/N_UNI
		except KeyError:
			return 10./(N_UNI * 10**len(word))

# probability of a bigram
def p2w(phrase, diacritic=True):
	if diacritic == False:
		try:
			return float(ND_BIGRAM[phrase])/N_ND_BI
		except KeyError:
			return 10./(N_ND_BI * 10**len(phrase))
	else:
		try:
			return float(BIGRAM[phrase])/N_BI
		except KeyError:
			return 10./(N_BI * 10**len(phrase))

# probability of a sequence of words
def pwords(words):
	return product([pw(w, diacritic=False) for w in words])

# conditional probability of a word and its previous word
def cpw(word, prev):
	try:
		return p2w(prev + " " + word)/pw(prev)
	except KeyError:
		return pw(word)
