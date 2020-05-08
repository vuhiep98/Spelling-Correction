import sys
from os.path import dirname, realpath
from math import log
from tqdm import tqdm
import re, json

from symspellpy.symspellpy import Verbosity
from jellyfish import jaro_winkler

sys.path.insert(0, dirname(dirname(realpath(__file__))))

from corrector.dictionary import Dictionary

class Corrector(Dictionary):

	def __init__(self):
		self.verbosity = Verbosity.ALL
		self.trigrams_weight = 1
		self.bigrams_weight = 1
		self.unigrams_weight = 1

	def _get_context(self, term):
		return self.context_dict.get(term, [])

	def _common_context(self, term_1, term_2):
		context_1 = self._get_context(term_1)
		context_2 = self._get_context(term_2)
		common = [c for c in context_1 if c in context_2]
		return len(common)

	def _gen_states(self, obs):
		states = {}
		new_obs = []
		for ob in obs:
			states[ob] = []
			if len(ob)==1 and re.match(r"[^aáàảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệiìíỉĩịoóòỏõọôồổỗộơờớỡợuùúũụưứửữựyỳýỷỹỵ]", ob):
				continue
			new_obs += [ob]

			# if len(ob)<=4: edit_distance=1
			# elif len(ob)>4 and len(ob)<=7: edit_distance=2
			if len(ob)<=7: edit_distance=2
			elif len(ob)>7: edit_distance=3

			candidates = self.symspell.lookup(phrase=ob,
			                                  verbosity=self.verbosity,
			                                  max_edit_distance=edit_distance,
			                                  include_unknown=True,
			                                  ignore_token=r'<START>|<END>|<num>')

			candidates_0 = sorted([c.term for c in candidates if c.distance==0],
			                      key=lambda x: -self._c1w(x))[:10]
			candidates_1 = sorted([c.term for c in candidates if c.distance==1],
			                      key=lambda x: -self._c1w(x))[:10]
			candidates_2 = sorted([c.term for c in candidates if c.distance==2],
			                      key=lambda x: -self._c1w(x))[:10]
			candidates_3 = sorted([c.term for c in candidates if c.distance==3],
			                      key=lambda x: -self._c1w(x))[:10]
			# candidates = sorted(candidates, key=lambda x: (-self._c1w(x.term),
			                                               # x.distance))[:20]
			candidates = candidates_0 + candidates_1 + candidates_2 + candidates_3
			# states[ob] = [c.term for c in candidates]
			states[ob] = candidates

		return new_obs, states
	
	def _trans(self, cur, prev, prev_prev=None):
		if prev_prev is None:
			return self.cpw(cur, prev)
		else:
			return self.cp3w(cur, prev, prev_prev)

	def _emiss(self, state, prev=None):
		if prev is None:
			return self.pw(state)
		else:
			return self.cpw(state, prev)

	def _viterbi_decoder(self, obs, states):
		V = [{}]
		path = {}

		for st in states[obs[0]]:
			V[0][st] = self._emiss(st)
			path[st] = [st]

		for i in range(1, len(obs)):
			V.append({})
			new_path = {}

			for st in states[obs[i]]:
				if i==1:
					prob, state = max([
						(V[i-1][prev_st]*self._trans(st, prev_st)*\
						 	self._emiss(st), prev_st)
						for prev_st in states[obs[i-1]]
					])

				else:
					prob, state = max([
						(V[i-1][prev_st]*self._trans(st, prev_st, prev_prev_st)*\
						 	self._emiss(st, prev_st), prev_st)
						for prev_st in states[obs[i-1]]
						for prev_prev_st in states[obs[i-2]]
					])

				V[i][st] = prob
				new_path[st] = path[state] + [st]

			path = new_path

		with open('data/viterbi_tracking.txt', 'w+', encoding='utf-8') as writer:
			# writer.write(json.dumps(path, indent=4, ensure_ascii=False) + '\n')
			writer.write(json.dumps(V, indent=4, ensure_ascii=False) + '\n')

		_, state = max([(V[-1][st], st) for st in states[obs[-1]]])

		return path[state]


	def correct(self, text):
		# obs = ['<START>'] + text.split() + ['<END>']
		obs = text.split()
		obs, states = self._gen_states(obs)
		result = self._viterbi_decoder(obs, states)
		# return [" ".join(r[1:-1]) for r in result]
		return " ".join(result)
