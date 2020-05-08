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
		threshold = 5
		
		with open(model_dir + file_name + ".txt", "r", encoding="utf-8") as reader:
			for line in tqdm(reader.readlines(), desc=file_name):
				line = line.replace("\n", "")
				key = line[:line.rindex(" ")]
				value = int(line[line.rindex(" ")+1:])
				if value >= threshold:
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
			max_dictionary_edit_distance=3,
			count_threshold=3,
		)
		cls.symspell.load_dictionary(
			corpus = model_dir + "unigrams.txt",
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
		cls._d = 0.75
	
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
	
	def _c1w(self, word):
		return self.uni_dict.get(word, 0)

	def _c2w(self, phrase):
		return self.bi_dict.get(phrase, 0)
	
	def _c3w(self, phrase):
		return self.tri_dict.get(phrase, 0)

	def pw(self, word):
		return float(self._c1w(word)+1)/self.n_uni
	
	@memo
	def cpw(self, word, prev):
		return float(self._c2w(prev + " " + word)+1)/(self._c1w(prev)+self.n_uni)

	def _k_coeff(self, cur, prev, prev_prev):
		k = {}
		k["2"] = (log(self._c2w(prev + ' ' + cur)+1)+1)/\
					(log(self._c2w(prev + ' ' + cur)+1)+2)
		k["3"] = (log(self._c3w(prev_prev + ' ' + prev + ' ' + cur)+1)+1)/\
					(log(self._c3w(prev_prev + ' ' + prev + ' ' + cur)+1)+2)
		return k

	def _delta_coeff(self, cur, prev, prev_prev):
		k = self._k_coeff(cur, prev, prev_prev)
		delta = {}
		delta["1"] = k["3"]
		delta["2"] = (1 - k["3"])*k["2"]
		delta["3"] = (1 - k["3"])*(1 - k["2"])
		return delta

	@memo
	def _lambda(self, prev, prev_prev=None):
		freq = 0
		if prev_prev is None:
			freq = sum([val for key, val in self.bi_dict.items() if prev==key.split()[0]])
			return (self._d/self._c1w(prev))*freq
		else:
			phrase = prev_prev + ' ' + prev
			freq = sum([val for key, val in self.tri_dict.items() 
			           if phrase==' '.join(key.split()[:2])])
			return (self._d/self._c2w(phrase))*freq

	@memo
	def _p_cont(self, cur, prev=None):
		if prev is None:
			freq = sum([val for key, val in self.bi_dict.items()
			           if cur==key.split()[1]])
			return float(freq)/self.n_bi
		else:
			phrase = prev + ' ' + cur
			freq = sum([val for key, val in self.tri_dict.items()
			           if phrase==' '.join(key.split()[-2:])])
			return float(freq)/self.n_tri

	# def _p3w(self, word, prev, prev_prev):
	# 		return float(self._c3w(prev_prev + " " + prev + " " + word)+1)/\
	# 				(self._c2w(prev_prev + " " + prev)+self.n_bi)

	@memo
	def cpw(self, cur, prev):
		try:
			first_term = float(max(self._c2w(prev + ' ' +cur) - self._d, 0))/\
						self._c1w(prev)
		except ZeroDivisionError:
			first_term = 0

		kn_lambda = self._lambda(prev)
		p_cont = self._p_cont(cur)

		return first_term + kn_lambda*p_cont

	@memo
	def cp3w(self, cur, prev, prev_prev):
		try:
			first_term = float(max(self._c3w(prev_prev + ' ' + prev + ' ' + cur) - self._d, 0))/\
						self._c2w(prev_prev + ' ' + prev)
		except ZeroDivisionError:
			first_term = 0

		kn_lambda = self._lambda(prev, prev_prev)
		p_cont = self._p_cont(cur, prev)

		return first_term + kn_lambda*p_cont

	# @memo
	# def cp3w(self, cur, prev, prev_prev):
	# 	delta = self._delta_coeff(cur, prev, prev_prev)
	# 	prob = delta["1"]*self._p3w(cur, prev, prev_prev) + \
	# 		   delta["2"]*self.cpw(cur, prev) + \
	# 		   delta["3"]*self.pw(cur)
	# 	return prob