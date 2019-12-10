from collections import Counter
from math import log
import re
from symspellpy.symspellpy import SymSpell, Verbosity
from tqdm import tqdm

from ultis import read_csv

class AutoCorrector:
    def __init__(self, max_edit_distance=2):
        self.uni_path = "model/unigrams.txt"
        self.bi_path = "model/bigrams.txt"
        self.tri_path = "model/trigrams.txt"
        self.symspell = SymSpell(max_dictionary_edit_distance=max_edit_distance)

    def __load_gram(self, path, n=1):
        ngram_counter = Counter()
        with open(path, "r", encoding="utf-8") as reader:
            for line in reader.readlines():
                line = line.replace("\n", "")
                contents = line.split()
                ngram_counter[" ".join(contents[0:n])] = int(contents[n])
        return ngram_counter
    
    def __count1w(self, word):
        return self.uni_dict[word] if word in self.uni_dict.keys() else 0

    def __count2w(self, phrase):
        return self.bi_dict[phrase] if phrase in self.bi_dict.keys() else 0
    
    def __count3w(self, phrase):
        return self.tri_dict[phrase] if phrase in self.tri_dict.keys() else 0
    
    def __p1w(self, word):
        if word not in self.uni_dict.keys():
            return -log(float(1)/self.n_uni)
        return -log(float(self.uni_dict[word])/self.n_uni)
    
    def __p2w(self, word, context):
        return -log(float(self.__count2w(word + " " + context) + 1)/
                                (self.uni_dict[context] + self.n_uni))
    
    def __p3w_1(self, word, context):
        return -log(float(self.__count3w(" ".join(context + [word])) + 1)/
                            (self.__count2w(" ".join(context)) + self.n_bi))

    def __p3w_2(self, word, context):
        left_prob = self.__p2w(context[0], word)
        right_prob = self.__p2w(word, context[1])
        return (left_prob + right_prob)/2
    
    def __p3w_3(self, word, context):
        return -log(float(self.__count3w(" ".join([word] + context)) + 1)/
                            (self.__count2w(" ".join(context)) + self.n_bi))
    
    def __P(self, word, left, right):
        p1 = 0
        p2 = 0
        p3 = 0
        if len(left)==0:
            if len(right)==1:
                p3 = self.__p2w(word, right[0])
            elif len(right)>=2:
                p3 = self.__p3w_3(word, right)
        
        if len(right)==0:
            if len(left)==1:
                p1 = self.__p2w(word, left[0])
            elif len(left)>=2:
                p1 = self.__p3w_1(word, left)
        
        if len(left)>=1 and len(right)>=1:
            p2 = self.__p3w_2(word, [left[-1], right[0]])

        return (p1+p2+p3)/3

    def __word_suggest(self, word, max_edit_distance=1):
        # suggestions = self.symspell.lookup(word, max_edit_distance=0, verbosity=Verbosity.ALL)
        # if not suggestions:
        suggestions = self.symspell.lookup(
                        word,
                        max_edit_distance=max_edit_distance,
                        verbosity=Verbosity.ALL)
        
        return [s._term for s in suggestions]

    def __test_none(self, text):
        return not text == '<start> <end>'
    
    def __pre_process(self, doc):
        doc = re.sub(r'\[\d+\]', '', doc)
        doc = re.sub(r'\[\w+\]', ' ', doc)  
        doc = re.sub(r'\d+((\.|\,)\d+)?', ' <number> ', doc)
        # paragraphs = doc.lower().split('\n')
        # clean_prgs = []
        # for p in paragraphs:
        #     sents = list(filter(None, re.split(r'\.|\?|!', p)))
        #     clean_sents = []
        #     for s in sents:
        #         s = re.sub('\,', ' ', s)
        #         s = re.sub('\"|\'|·|•', ' ', s)
        #         s = '<start> ' + s.strip() + ' <end>'
        #         s = re.sub('\s{2,}', ' ', s)
        #         clean_sents.append(s)
        #     clean_prgs.append(list(filter(self.__test_none, clean_sents)))
        # return list(filter(None, clean_prgs))
        doc = re.sub('\,', ' ', doc)
        doc = re.sub('\"|\'|·|•', ' ', doc)
        # doc = '<start> ' + doc.strip() + ' <end>'
        doc = re.sub('\s{2,}', ' ', doc)
        return doc
    
    def load(self):
        self.uni_dict = self.__load_gram(self.uni_path, n=1)
        self.n_uni = sum(self.uni_dict.values())
        self.bi_dict = self.__load_gram(self.bi_path, n=2)
        self.n_bi = sum(self.bi_dict.values())
        self.tri_dict = self.__load_gram(self.tri_path, n=3)
        self.n_tri = sum(self.tri_dict.values())
        self.symspell.load_dictionary(self.uni_path, term_index=0, count_index=1, encoding="utf-8")
    
    def statistic(self):
        print("Model's statistic\n--------\n")
        print("Number of unigrams: " + str(self.n_uni))
        print("Number of bigrams: " + str(self.n_bi))
        print("Number of trigrams: " + str(self.n_tri))

    def __correct_sentence(self, sentence):
        words = sentence.lower().split()
        foward_corrected_words = words
        for i in range(len(words)):
            if i==0 or i==len(words)-1:
                # for s in suggestions:
                #     prob[s] = self.__P(s, left=[], right=words[i+1:min(len(words), i+3)])
                continue
            else:
                suggestions = self.__word_suggest(words[i])
                prob = {}
                if i==1:
                    for s in suggestions:
                        prob[s] = self.__P(s, left=[words[i-1]], right=words[i+1:min(len(words), i+3)])
                elif i==len(words)-2:
                    for s in suggestions:
                        prob[s] = self.__P(s, left=words[max(i-2, 0):i], right=[words[i+1]])
                else:
                    for s in suggestions:
                        prob[s] = self.__P(s, words[i-2:i], words[i+1:i+3])
            
                correct_word = min(prob.keys(), key=prob.get)
                foward_corrected_words[i] = correct_word

        # backward_corrected_words = foward_corrected_words
        # i = len(foward_corrected_words)-1
        # while i >= 0:
        #     suggestions = self.__word_suggest(foward_corrected_words[i])
        #     prob = {}
        #     if i==len(foward_corrected_words)-1:
        #         for s in suggestions:
        #             prob[s] = self.__P(s, left=foward_corrected_words[max(i-2, 0):i],
        #                             right=[])
        #     elif i==len(foward_corrected_words)-2:
        #         for s in suggestions:
        #             prob[s] = self.__P(s, left=foward_corrected_words[max(i-2, 0): i],
        #                             right=[foward_corrected_words[i+1]])
        #     elif i==1:
        #         for s in suggestions:
        #             prob[s] = self.__P(s, left=[foward_corrected_words[i-1]],
        #                             right=foward_corrected_words[i+1:i+3])
        #     elif i==0:
        #         for s in suggestions:
        #             prob[s] = self.__P(s, left=[], right=foward_corrected_words[i+1:i+3])
        #     else:
        #         for s in suggestions:
        #             prob[s] = self.__P(s, left=foward_corrected_words[i-2:i],
        #                             right=foward_corrected_words[i+1:i+3])
            
        #     correct_word = min(prob.keys(), key=prob.get)
        #     backward_corrected_words[i] = correct_word
        #     i -= 1
        
        # corrected_sentence = " ".join(backward_corrected_words[::-1])
        corrected_sentence = " ".join(foward_corrected_words)
        corrected_sentence = corrected_sentence.replace("<start>", "")
        corrected_sentence = corrected_sentence.replace("<end>", "")
        return corrected_sentence.strip()
    
    def correct(self, doc):
        processed_doc = self.__pre_process(doc)
        # result = []
        # for p in processed_doc:
        #     result.append(".".join([self.__correct_sentence(s) for s in p]))
        # return result
        return self.__correct_sentence(processed_doc)
    
    def correct_from_file(self, input_file):
        data = read_csv(input_file)
        result = [self.correct(d) for d in data['error_sentence']]
        return result, data['correct_sentence'].values.tolist()

if __name__ == "__main__":

    corrector = AutoCorrector()
    print("Loading components...")
    corrector.load()
    print("Finished")
    # corrector.test()
    
