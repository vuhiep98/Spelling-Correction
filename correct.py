from ultis import edit
from viterbi import viterbi_decoder

def gen_states(obs):
	states = {}
	for ob in obs:
		states[ob] = edit(ob)
	return states

def correct(text):
	obs = text.split()
	states = gen_states(obs)
	result = viterbi_decoder(obs, states)
	return " ".join(result)
