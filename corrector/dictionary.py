import sys
from os.path import dirname, realpath
from math import log, log10
from tqdm import tqdm
import json
from symspellpy.symspellpy import SymSpell

sys.path.insert(0, dirname(dirname(realpath(__file__))))

from corrector.ultis import product, memo


model_dir="model/new/"
diacritic_adder="model/diacritic_adder.txt"


class Dictionary:

	def __init__(self):
		# self.verbosity = Verbosity.ALL
		pass
	
	@classmethod
	def _from_text(cls, file_name="unigrams"):
		dct = {}
		n = 0
		
		with open(model_dir + file_name + ".txt", "r", encoding="utf-8") as reader:
			for line in tqdm(reader.readlines(), desc=file_name):
				line = line.replace("\n", "")
				key = line[:line.rindex(" ")]
				value = int(line[line.rindex(" ")+1:])
				dct[key] = value
				n += value
		return dct, n
	
	def _common_contexts(self, word, suggestion):
		word_contexts = self.context_dict.get(word, [])
		suggestion_contexts = self.context_dict.get(suggestion, [])
		return sum([suggestion_contexts[c] for c in suggestion_contexts 
		           	if c in word_contexts and suggestion_contexts[c] >= word_contexts[c]])
	
	@classmethod
	def load_symspell(cls):
		cls.symspell = SymSpell(
			max_dictionary_edit_distance=2,
			count_threshold=20,
		)
		cls.symspell.load_dictionary(
			corpus = model_dir + "unigrams.txt",
			# corpus = "model/non_diacritic_model/unigrams.txt",
			term_index = 0,
			count_index = 1,
			separator=" ",
			encoding="utf-8"
		)
	
	@classmethod
	def load_dict(cls):
		cls.uni_dict, cls.n_uni = cls._from_text(file_name="unigrams")
		cls.bi_dict, cls.n_bi = cls._from_text(file_name="bigrams")
		cls.tri_dict, cls.n_tri = cls._from_text(file_name="trigrams")
		# cls.uni_segment, cls.n_uni_segment = cls._from_text(file_name="non_diacritic_model/unigrams")
		# cls.bi_segment, cls.n_bi_segment = cls._from_text(file_name="non_diacritic/bigrams") 
	
	@classmethod
	def load_context_dict(cls):
		with open(model_dir + "context_dict.txt", "r", encoding="utf-8") as reader:
			try:
				cls.context_dict = json.load(reader)
			except FileNotFoundError:
				print("Context dictionary does not exist")

	@classmethod
	def load_diacritic_adder(cls):
		with open(diacritic_adder, "r", encoding="utf-8") as reader:
			cls.diacritic_adder = json.load(reader.read())

	@memo
	def pw_segment(self, word):
		try:
			return float(self.uni_segment[word])/self.n_uni_segment
		except KeyError:
			return 10./(self.n_uni_segment * 10**len(word))
	
	@memo
	def pw(self, word):
		try:
			return float(self.uni_dict[word])/self.n_uni
		except KeyError:
			return 10./(self.n_uni * 10**len(word))

	@memo
	def p2w(self, phrase):
		try:
			return float(self.bi_dict[phrase])/self.n_bi
		except:
			return 10./(self.n_bi * 10**len(phrase))
	
	@memo
	def p3w(self, phrase):
		try:
			return float(self.tri_dict[phrase])/self.n_tri
		except KeyError:
			return 10./(self.n_tri * 10**len(phrase))

	def pwords(self, words):
		return product([self.pw(word) for word in words])

	def pwords_segment(self, words):
		return product([self.pw_segment(word) for word in words])
	
	def cpw(self, word, prev):
		try:
			return self.p2w(prev + " " + word)/self.pw(prev)
		except KeyError:
			return self.pw(word)
	
	def cp3w(self, word, prev, prev_prev):
		try:
			return self.p3w(prev_prev + " " + prev + " " + word)/self.p2w(prev_prev + " " + prev)
		except KeyError:
			return self.p2w(prev_prev + " " + prev)