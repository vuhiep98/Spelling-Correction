from ultis import product
from math import log, log10

class Dictionary:

	def __init__(self, model_dir="model/"):
		self.model_dir = model_dir
		self._load_dict()
	
	def _from_text(self, file_name="unigrams.txt"):
		dct = {}
		n = 0
		
		with open(self.model_dir + file_name, "r", encoding="utf-8") as reader:
			for line in reader.readlines():
				line = line.replace("\n", "")
				key = line[:line.rindex(" ")]
				value = int(line[line.rindex(" ")+1:])
				dct[key] = value
				n += value
		return dct, n
	
	def _load_dict(self):
		self.uni_dict, self.n_uni = self._from_text(file_name="unigrams.txt")
		self.bi_dict, self.n_bi = self._from_text(file_name="bigrams.txt")
		self.tri_dict, self.n_tri = self._from_text(file_name='trigrams.txt')
	
	def pw(self, word):
		try:
			return float(self.uni_dict[word])/self.n_uni
		except KeyError:
			return 10./(self.n_uni * 10**len(word))

	def p2w(self, phrase):
		try:
			return float(self.bi_dict[phrase])/self.n_bi
		except:
			return 10./(self.n_bi * 10**len(phrase))
	
	def p3w(self, phrase):
		try:
			return float(self.tri_dict[phrase])/self.n_tri
		except KeyError:
			return 10./(self.n_tri * 10**len(phrase))
	
	def pwords(self, words):
		return product([self.pw(word) for word in words])
	
	def cpw(self, word, prev):
		try:
			return self.p2w(prev + " " + word)/self.pw(prev)
		except KeyError:
			return self.pw(word)