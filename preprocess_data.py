import os, re, string
from tqdm import tqdm
from collections import Counter

def encode_numbers(text):
	tokens = text.split()
	for i, t in enumerate(tokens):
		if any([d in t for d in string.digits]):
			tokens[i] = '<num>'
	text = ' '.join(tokens)
	return text

def preprocess(text):
	text = text.strip().lower()
	text = encode_numbers(text)
	# text = re.sub('\n|\.$|"|”|“|\'|\(|\)|,|:|;|(\.{2,})|…', '', text)
	# text = re.sub('\.\s+', ' ', text)
	# text = re.sub('\s{2,}', ' ', text)
	# text = re.sub('\s–\s|–\s|\s–|\s-\s|-\s|\s-', ' ', text)
	return text
	

def read_about(folder_number):
	abouts = []
	for i in tqdm(range(folder_number*10000, (folder_number+1)*10000), desc=str(folder_num)):
		file_directory = 'STM project/data_original_files' + \
						  str(folder_number*10000) + '-' + \
						  str((folder_number+1)*10000-1) + '/' + \
						  str(i) + '_about.txt'
		if os.path.isfile(file_directory):
			reader = open(file_directory, 'r', encoding='utf-8')
			abouts += [preprocess(' '.join(reader.readlines()))]
	return abouts

def drop_na(sent):
	return True if sent not in ['', '#'] else False


def read_content(content_path):
	if os.path.isfile(content_path):
		sentences = []
		with open(content_path, 'r', encoding='utf-8') as reader:
			content = reader.read()
			# content = re.sub('\s{2,}', ' ', content)
			content = re.sub('\n', ' ', content)
			lines = re.split('\s{3,}', content)
#             lines = re.split("\n", reader.read())
			for line in lines:
				if '|' in line: continue
		#         unigrams.append(re.findall('\w+', line))
		#         line = re.sub('\(|\)|:|(\.$)|(^\d+\.)|/^\d\./gm', '', line.lower())
		#         unigrams += line.split()
#                 line = preprocess(line)
				sents = []
				line = encode_numbers(line)
				for sent in re.split('\.|\?|:', line):
#                     sent = re.sub('(^/)|(\?)', '', sent)
#                     sent = sent.strip()

					sent = sent.lower()
					sent = " ".join(re.findall('<num>|\w+', sent))
					sents.append(sent)
				sentences += sents
		return list(filter(drop_na, sentences))
	else:
		return []


def preprocess_data():
	start = 41
	end = 42

	unigrams = {}
	# if os.path.isfile('STM_n_gram_models/new_content_models/unigrams.txt'):
	# 	with open('STM_n_gram_models/new_content_models/unigrams.txt', 'r', encoding='utf-8') as reader:
	# 		for line in reader.readlines():
	# 			unis = line.replace('\n', '').split()
	# 			unigrams[unis[0]] = int(unis[1])
	# 	reader.close()

	bigrams = {}
	# if os.path.isfile('STM_n_gram_models/new_content_models/bigrams.txt'):
	# 	with open('STM_n_gram_models/new_content_models/bigrams.txt', 'r', encoding='utf-8') as reader:
	# 		for line in reader.readlines():
	# 			bis = line.replace('\n', '').split()
	# 			bigrams[bis[0]+' '+bis[1]] = int(bis[2])
	# 	reader.close()

	trigrams = {}
	# if os.path.isfile('STM_n_gram_models/new_content_models/trigrams.txt'):
	# 	with open('STM_n_gram_models/new_content_models/trigrams.txt', 'r', encoding='utf-8') as reader:
	# 		for line in reader.readlines():
	# 			tris = line.replace('\n', '').split()
	# 			trigrams[tris[0]+' '+tris[1]+' '+tris[2]] = int(tris[3])
	# 	reader.close()

	for i in range(start, end+1):
		for j in tqdm(range(i*10000, (i+1)*10000), desc=str(i), ascii=True):
			for sent in read_content('STM Project/data_original_files' + str(i*10000) + '-' + str((i+1)*10000-1) + \
									 '/' + str(j) + '_content.txt'):
				words = ['<START>'] + sent.split() + ['<END>']
				for index, w in enumerate(words):
					if index < len(words)-2:
						if w+' '+words[index+1]+' '+words[index+2] in trigrams: trigrams[w+' '+words[index+1]+' '+words[index+2]] += 1
						else: trigrams[w+' '+words[index+1]+' '+words[index+2]] = 1
					if index < len(words)-1:
						if w+' '+words[index+1] in bigrams: bigrams[w+' '+words[index+1]] += 1
						else: bigrams[w+' '+words[index+1]] = 1
					if w in unigrams: unigrams[w] += 1
					else: unigrams[w] = 1

	cnt_uni = sorted(Counter(unigrams).items(), key=lambda x: x[1], reverse=True)
	cnt_bi = sorted(Counter(bigrams).items(), key=lambda x: x[1], reverse=True)
	cnt_tri = sorted(Counter(trigrams).items(), key=lambda x: x[1], reverse=True)

	# with open('STM_n_gram_models/new_content_models/unigrams.txt', 'a+', encoding='utf-8') as writer:
	# 	for uni in cnt_uni:
	# 		writer.write(str(uni[0]) + ' ' + str(uni[1]) + '\n')
	# writer.close()

	# with open('STM_n_gram_models/new_content_models/bigrams.txt', 'a+', encoding='utf-8') as writer:
	# 	for bi in cnt_bi:
	# 		writer.write(str(bi[0]) + ' ' + str(bi[1]) + '\n')
	# writer.close()

	# with open('STM_n_gram_models/new_content_models/trigrams.txt', 'a+', encoding='utf-8') as writer:
	# 	for tri in cnt_tri:
	# 		writer.write(str(tri[0]) + ' ' + str(tri[1]) + '\n')

	return cnt_uni

if __name__ == '__main__':
	content = read_content('data/31288_content.txt')
	with open('output.txt', 'w+', encoding='utf-8') as writer:
		for c in content:
			writer.write(str(c) + '\n')