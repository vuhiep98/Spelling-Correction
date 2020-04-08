from flask import Flask, render_template, request, jsonify
import json

from corrector.dictionary import Dictionary
from corrector.segment import Segmentor
from corrector.correct import Corrector
from corrector.ultis import encode_numbers, decode_numbers, unikey_typos_handler

app = Flask(__name__, static_folder='static')

dictionary = Dictionary()
segmentor = Segmentor()
corrector = Corrector()

dictionary.load_dict()
dictionary.load_symspell()
# dictionary.load_context_dict()


@app.route('/query_auto_correction')
def get_home():
	return render_template('index.html', title='Query Auto Correction')

@app.route('/correct', methods=['POST'])
def correct():
	query = request.json.get('query').lower()
	query, numbers = encode_numbers(query)
	result = unikey_typos_handler(query)
	result = segmentor.segment(result)
	result = corrector.correct(result)
	result = decode_numbers(result, numbers)
	return result
