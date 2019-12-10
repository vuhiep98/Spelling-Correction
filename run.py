from auto_correct import AutoCorrector
from tqdm import tqdm
# from ultis import evaluate


corrector = AutoCorrector(max_edit_distance=1)
print('Loading corrector...')
corrector.load()
print('Finish loading')
print('Start predicting')
# for i in tqdm(range(100)):
#     doc = "\n".join(open('Wiki_test_file/test_' + str(i) + '.txt', 'r', encoding='utf-8').readlines()[:5])
#     corrected_doc = "\n".join(corrector.correct(doc))
#     open('result_5_line/correct_' + str(i) + '.txt', 'w+', encoding='utf-8').write(corrected_doc)
print(corrector.correct('câu lạc bộ arsenal thắng 5 bàn'))
