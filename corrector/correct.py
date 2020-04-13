import sys
from os.path import dirname, realpath
from math import log10
from tqdm import tqdm
import re, json
from symspellpy.symspellpy import Verbosity

sys.path.insert(0, dirname(dirname(realpath(__file__))))

from corrector.dictionary import Dictionary

class Corrector(Dictionary):

	def __init__(self):
		self.verbosity = Verbosity.ALL

	def _gen_states(self, obs):
		states = {}
		new_obs = []
		for i, ob in enumerate(obs):
			states[ob] = []
			if len(ob)==1 and re.match(r"[^aáàảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệiìíỉĩịoóòỏõọôồổỗộơờớỡợuùúũụưứửữựỳýỷỹỵ]", ob):
				continue
			new_obs += [ob]
			candidates = self.symspell.lookup(phrase=ob,
			                                  verbosity=self.verbosity,
			                                  max_edit_distance=2,
			                                  include_unknown=True,
			                                  ignore_token=r'<START>|<END>|<num>')

			candidates = sorted(candidates, key=lambda x:(x.distance, -self.uni_dict.get(x.term, 0)))[:30]
			states[ob] = [c.term for c in candidates]
		return new_obs, states
	
	def _trans(self, cur, prev, prev_prev=None):
		if prev_prev is None:
			return -log10(self.cpw(cur, prev))
		else:
			return -log10(self.cp3w(cur, prev, prev_prev))

	def _emiss(self, state):
		return -log10(self.pw(state))

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
					prob, state = min([
						(V[i-1][prev_st] + self._trans(st, prev_st) + self._emiss(st), prev_st)
						for prev_st in states[obs[i-1]]
					])

				else:
					prob, state = min([
						(V[i-1][prev_st] + self._trans(st, prev_st, prev_prev_st) + self._emiss(st), prev_st)
						for prev_st in states[obs[i-1]]
						for prev_prev_st in states[obs[i-2]]
					])

				V[i][st] = prob
				new_path[st] = path[state] + [st]

			path = new_path

		with open('data/viterbi_tracking.txt', 'w+', encoding='utf-8') as writer:
			# writer.write(json.dumps(path, indent=4, ensure_ascii=False) + '\n')
			writer.write(json.dumps(V, indent=4, ensure_ascii=False) + '\n')

		_, state = min([(V[-1][st], st) for st in states[obs[-1]]])

		return path[state]


	def correct(self, text):
		# obs = ['<START>'] + text.split() + ['<END>']
		obs = text.split()
		obs, states = self._gen_states(obs)
		result = self._viterbi_decoder(obs, states)
		# return [" ".join(r[1:-1]) for r in result]
		return " ".join(result)
