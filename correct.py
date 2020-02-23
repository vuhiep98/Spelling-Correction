from ultis import edit
from viterbi import viterbi_decoder

def gen_states(obs):
	states = {}
	for ob in obs:
		if ob == '<START>' or ob == '<END>':
			states[ob] = [ob]
		else:
			states[ob] = edit(ob)
	return states

def correct(text):
	obs = ['<START>'] + text.split() + ['<END>']
	states = gen_states(obs)
	result = viterbi_decoder(obs, states)
	return " ".join(result[1:-1])
