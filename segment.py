from ultis import memo, remove_diacritics
from dictionary import Dictionary
from math import log10

class Segmentator:

	def __init__(self):
		self.dictionary = Dictionary()
	
	def _combine(self, Pfirst, first, rest):
		return Pfirst + rest[0], [first] + rest[1]
	
	def _splits(self, text, max_word_length=20):
		return [(text[:i+1], text[i+1:]) for i in range(min(len(text), max_word_length))]

	@memo
	def _segment_token(self, text):
		if not text:
			return []
		candidates = ([first] + self._segment_token(rest) for first, rest in self._splits(text))
		return max(candidates, key=self.dictionary.pwords)
	
	@memo
	def _segment_token_2(self, text, prev="<START>"):
		if not text:
			return 0.0, []
		candidates = [self._combine(-log10(self.dictionary.cpw(first, prev)), first, self._segment_token_2(rest, first))
				for first, rest in self._splits(text)]
		return min(candidates)

def segment(self, text):
	# text = remove_diacritics(text)
	text = "".join(text.split())
	result = " ".join(self._segment_token(text))
	return result