from flask import Flask, render_template, request, jsonify
import json
import pandas as pd
from tqdm import tqdm

from corrector.dictionary import Dictionary
from corrector.segment import Segmentor
from corrector.correct import Corrector
from corrector.diacritic import DiacriticAdder
from corrector.ultis import encode_numbers, decode_numbers, unikey_typos_handler

app = Flask(__name__, static_folder='static')

dictionary = Dictionary()
# segmentor = Segmentor()
corrector = Corrector()

dictionary.load_dict()
dictionary.create_cont_dict()
dictionary.load_symspell()
dictionary.load_diacritic_adder()
dictionary.load_context_dict()

@app.route('/query_auto_correction')
def get_home():
	return render_template('index.html', title='Query Auto Correction')

@app.route('/correct', methods=['POST'])
def correct():
	query = request.json.get('query').lower()
	print(query)
	query, numbers = encode_numbers(query)
	result = unikey_typos_handler(query)
	# result = segmentor.segment(result)
	corrected_result = corrector.correct(result)
	# diacritic_added_result = diacritic_adder.add_diacritic(result)
	corrected_result['result'] = decode_numbers(corrected_result['result'], numbers)
	# diacritic_added_result['result'] = decode_numbers(diacritic_added_result['result'], numbers)
	return json.dumps({
	    'corrected': corrected_result
	    # 'diacritic_added': diacritic_added_result
	})

@app.route('/correct_file')
def correct_file():
	inputs = pd.read_csv('testing_file.csv')
	wrong_predict = []
	results = []
	for i, row in tqdm(inputs.iterrows()):
		query = row['query']
		query, numbers = encode_numbers(query.lower())
		result = unikey_typos_handler(query)
		result = segmentor.segment(result)
		corrected_result = corrector.correct(result)
		# diacritic_added_result = diacritic_adder.add_diacritic(result)
		corrected_result['result'] = decode_numbers(corrected_result['result'], numbers)
		# diacritic_added_result['result'] = decode_numbers(diacritic_added_result['result'], numbers)
		results.append([row['query'],
		               row['correct'],
		               corrected_result['result'],
		               corrected_result['prob']])
		               # diacritic_added_result['result'],
		               # diacritic_added_result['prob']])
		if corrected_result['result']!=row['correct']:
		# and diacritic_added_result['result']!=row['correct']:
			wrong_predict.append([row['query'],
		               row['correct'],
		               corrected_result['result'],
		               corrected_result['prob']])
		               # diacritic_added_result['result'],
		               # diacritic_added_result['prob']])
	pd.DataFrame(results, columns=['query',
					               'correct',
					               'corrected',
					               'corrected_prob']).to_csv('correct_result.csv', index=False)
	             # 'diacritic_added',
	             # 'diacritic_added_prob']).to_csv('correct_result.csv', index=False)
	pd.DataFrame(wrong_predict, columns=['query',
	             'correct',
	             'corrected',
	             'corrected_prob']).to_csv('wrong_correct_result.csv', index=False)
	
	             # 'diacritic_added',
	             # 'diacritic_added_prob']).to_csv('wrong_correct_result.csv', index=False)
	
	return '<h3>FINISH<h3>'
