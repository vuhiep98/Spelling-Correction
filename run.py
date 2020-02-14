import pandas as pd
from ultis import unikey_typos_handler, encode_numbers, decode_numbers
from segment import segment
from correct import correct

text = "chicucthuequa12"

text, numbers = encode_numbers(text)
result = unikey_typos_handler(text)
result = segment(result)
# result = correct(result)
result = decode_numbers(result, numbers)
print(result)
