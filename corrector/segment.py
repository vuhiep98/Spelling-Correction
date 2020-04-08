import sys
from os.path import dirname, realpath
from math import log10
from tqdm import tqdm

sys.path.insert(0, dirname(dirname(realpath(__file__))))

from corrector.ultis import memo, remove_diacritics
from corrector.dictionary import Dictionary

class Segmentor(Dictionary):

	def __init__(self):
		pass
	
	# def _combine(self, Pfirst, first, rest):
	# 	return Pfirst + rest[0], [first] + rest[1]
	
	# def _splits(self, text, max_word_length=20):
	# 	return [(text[:i+1], text[i+1:]) for i in range(min(len(text), max_word_length))]

	# @memo
	# def _segment_token(self, text):
	# 	if not text:
	# 		return []
	# 	candidates = ([first] + self._segment_token(rest) for first, rest in self._splits(text))
	# 	return max(candidates, key=self.pwords_segment)
	
	# @memo
	# def _segment_token_2(self, text, prev="<START>"):
	# 	if not text:
	# 		return 0.0, []
	# 	candidates = [self._combine(-log10(self.cpw(first, prev)), first, self._segment_token_2(rest, first))
	# 			for first, rest in self._splits(text)]
	# 	return min(candidates)

	def segment(self, text):
		tokens = text.split()
		for i in range(len(tokens)):
			if tokens[i] not in self.uni_dict:
				segment = self.symspell.word_segmentation(
				    phrase=tokens[i],
				    max_edit_distance=1,
				    max_segmentation_word_length=15
				)[1]
				tokens = tokens[:i] + segment.split() + tokens[i+1:]
		return " ".join(tokens)