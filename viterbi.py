from dictionary import cpw, pw, UNIGRAM
from math import log10


def trans(cur_state, prev_state):
	return -log10(cpw(cur_state, prev_state))

def emiss(cur_state):
	return -log10(pw(cur_state))

def viterbi_decoder(obs, states):

	V = [{}]
	path = [{}]

	read_out_path = []

	for st in states[obs[0]]:
		V[0][st] = 0
		path[0][st] = st

	for i in range(1, len(obs)):

		V.append({})
		path.append({})

		for st in states[obs[i]]:

			if obs[i-1] in UNIGRAM:
				prob, state = min(
					[(V[i-1][obs[i-1]] + trans(st, obs[i-1]) + emiss(st), obs[i-1])]
				)
			else:
				prob, state = min(
					[(V[i-1][prev_st] + trans(st, prev_st) + emiss(st), prev_st)
							for prev_st in states[obs[i-1]]]
				)

			V[i][st] = prob
			path[i][st] = state

	with open('viterbi_tracking.txt', 'w+', encoding='utf-8') as writer:
		for i in range(len(V)):
			writer.write(str(V[i]) + '\n')

	prob, state = min([(V[-1][st], st) for st in states[obs[-1]]])
	read_out_path.append(state)

	for i in range(len(obs)-2, -1, -1):
		prob, state = min([(V[i][st], st) for st in states[obs[i]]])
		read_out_path.append(state)

	read_out_path.reverse()

	return read_out_path

def bi_viterbi(obs, states):

	# V = [{}]
	# path = []

	# for st in states[obs[0]]:
	# 	V[0][st] = 0

	# for i in range(1, len(obs)):

	# 	V.append({})

	# 	for st in states(obs[i]):
	# 		if obs[i] in UNIGRAM:
	# 			prob, state = min(
	# 				[(V[i-1][obs[i-1]] + trans(st, obs[i]), obs[i])]
	# 				)
	# 		else:
	# 			prob, state = min(
	# 				[(V[i-1][prev_st] + trans(st, prev_st), prev_st)
	# 					for prev_st in states[obs[i-1]]]
	# 				)
	# 		V[i][st] = prob + emiss(st)
	# 	path.append(state)
	pass



