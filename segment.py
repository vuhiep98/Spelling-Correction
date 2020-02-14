from ultis import memo, encode_numbers, decode_numbers, remove_diacritics
from dictionary import cpw, pwords
from math import log10

# combine
def combine(Pfirst, first, rest):
	return Pfirst + rest[0], [first] + rest[1]

# split strings
def splits(text, max_word_length=20):
	return [(text[:i+1], text[i+1:]) for i in range(min(len(text), max_word_length))]

# segment token
@memo
def segment_tokens(text):
	if not text:
		return []
	candidates = ([first] + segment_tokens(rest) for first, rest in splits(text))
	return max(candidates, key=pwords)

# segment token based on conditional probability
@memo
def segment_tokens_2(text, prev="<START>"):
	if not text:
		return 0.0, []
	candidates = [combine(-log10(cpw(first, prev)), first, segment_tokens_2(rest, first))
			for first, rest in splits(text)]
	return min(candidates)

# segment wrapper
def segment(text):
	text = remove_diacritics(text)
	text = "".join(text.split())
	result = " ".join(segment_tokens(text))
	return result