import random
import pandas as pd

character_dict = 'aáàảãạăằắẳẵặâầấẩẫậ' + \
				 'bcdđ' + 'eèéẻẽẹêềếểễệ' + \
				 'gh' + 'iìíỉĩị' + 'klmn' + \
				 'oóòỏõọôồổỗộơờớỡợ' + 'pqrst' + \
				 'uùúũụưứửữự' + 'vwx' + 'yỳýỷỹỵ' + 'z '
				 
max_error_rate = 0.2

def get_random_character():
	return random.choice(character_dict)

def get_position(term):
	return random.choice(list(range(len(term))))

def insert(term, character, position):
	return term[:position] + character + term[position:]

def delete(term, position):
	return term[:position] + term[position+1:]

def change(term, character, position):
	return term[:position] + character + term[position+1:]

def transpose(term, index_1, index_2):
	return term[:index_1] + term[index_2] + term[index_1+1:index_2] + term[index_1] + term[index_2+1:]
	return term

def create_token_error(term):
	error_type = random.choice([1, 2, 3, 4])
	if error_type == 1:
		random_char = get_random_character()
		random_pos = get_position(term)
		term = insert(term, random_char, random_pos)
	elif error_type == 2:
		random_pos = get_position(term)
		term = delete(term, random_pos)
	elif error_type == 3:
		random_char = get_random_character()
		random_pos = get_position(term)
		term = change(term, random_char, random_pos)
	elif error_type == 4:
		index_1 = get_position(term)
		index_2 = get_position(term)
		while index_2 == index_1:
			index_2 = get_position(term)
		term = transpose(term, index_1, index_2)
	return term

def create_query_error(query):
	terms = query.split()
	error_num = int(random.uniform(0, max_error_rate) * len(terms))+1
	for i in range(error_num):
		error_type = random.choice([1, 2])
		index_error_term = random.choice(list(range(len(terms))))
		if error_type == 1:
			terms[index_error_term] = create_token_error(terms[index_error_term])
			error_query = ' '.join(terms)
		else:
			error_query = ' '.join(terms[:index_error_term]) + ' '.join(terms[index_error_term:]) 
	return error_query

if __name__ == '__main__':
	# open('test.txt', 'w+', encoding='utf-8').write(create_query_error('điện thoại di động'))
	correct_query = []
	with open('testing_input.txt', 'r', encoding='utf-8') as reader:
		for line in reader.readlines():
			correct_query.append(line.replace('\n', ''))
	error_query = [create_query_error(query) for query in correct_query]
	testing_file = pd.DataFrame([[error, correct] for error, correct in zip(error_query, correct_query)]).to_csv(
	                    'testing_file.csv', index=False)
