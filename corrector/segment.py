import sys
from os.path import dirname, realpath
from math import log10
from tqdm import tqdm
from symspellpy.symspellpy import Verbosity

sys.path.insert(0, dirname(dirname(realpath(__file__))))

from corrector.ultis import memo, remove_diacritics
from corrector.dictionary import Dictionary

class Segmentor(Dictionary):

	def __init__(self):
		pass
	
	# def _P(self, text):
	# 	if len(text.split())==1:
	# 		return self.uni_dict.get(text, 0)
	# 	elif len(text.split())==2:
	# 		return self.bi_dict.get(text, 0)
	# 	else:
	# 		return 0

	def _split(self, text):
		return [(text[:i], text[i:]) for i in range(1, len(text))]

	# def _find_can(self, term):
	# 	can = self.symspell.lookup(term, max_edit_distance=1, verbosity=Verbosity.ALL)
	# 	return sorted(can, key=lambda x: (x.distance, -self._P(x.term)))[:5]

	# def _best_split(self, token):
	# 	best_seg = ''
	# 	for can in self._split(token):
	# 		L, R = can.split()
	# 		L_can = self._find_can(L)
	# 		R_can = self._find_can(R)
	# 		seg = sorted([l.term + ' ' + r.term for l in L_can for r in R_can], key=lambda x: -self._P(x))
	# 		if seg == []:
	# 			continue     
	# 		if self._P(seg[0]) > self._P(best_seg):
	# 			best_seg = seg[0]
	# 	if self._P(best_seg) > self._P(token):
	# 		L, R = best_seg.split()
	# 		return self._best_split(L) + ' ' + self._best_split(R)
	# 	else:
	# 		return token

	def _segment_token(self, text):
		if not text:
			return []
		candidates = [text] + [first + ' ' + self._segment_token(rest)
						for first, rest in self._split(text)]
		return max(candidates, key=self.p_sentence)

	def segment(self, text):
		# new_text = ''
		# while True:
		# 	tokens = text.split()
		# 	new_text = ' '.join([self._best_split(t) for t in tokens])
		# 	if new_text == text:
		# 		break
		# 	else:
		# 		text = new_text
		# return new_text
		return ' '.join([self._segment_token(t) for t in text.split() if t not in self.uni_dict])