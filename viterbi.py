from dictionary import cpw, pw
from math import log10


def trans(cur_state, prev_state):
	return -log10(cpw(cur_state, prev_state))

def emiss(cur_state):
	return -log10(pw(cur_state))

def viterbi_decoder(obs, states):

	V = [{}]
	path = []

	for st in states[obs[0]]:
		V[0][st] = 0

	for i in range(1, len(obs)):

		V.append({})
		for st in states[obs[i]]:
			prob, state = min(
				[(V[i-1][prev_st] + trans(st, prev_st), prev_st) 
						for prev_st in states[obs[i-1]]]
			)
			V[i][st] = prob + emiss(st)
		path.append(state)

	prob, state = min([(V[-1][st], st) for st in states[obs[-1]]])
	path.append(state)

	return path



