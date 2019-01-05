
from nlu_api import NluApi

from collections import namedtuple

ResultTuple = namedtuple("result", "index originalQ originalA tokenizedQ tokenizedA spellcheckedQ".split())


def stat_to_string(utterance):
    response_dict = NluApi(utterance)
    print('inputstring\t\t', response_dict['parserOutputs'][1]['wordgraph_obj']['inputString'])
    print('flat\t\t', response_dict['parserOutputs'][1]['wordgraph_flat'])
    # print('parserString\t\t', response_dict['parserOutputs'][1]['wordgraph_obj']['parserString'])

def extractSpellCheck(utterance):
    response_dict = NluApi(utterance)
    original = response_dict['parserOutputs'][1]['wordgraph_obj']['inputString']
    featurized = response_dict['parserOutputs'][1]['wordgraph_flat']
    return (original, featurized)


#0 49:
#1 original
#2 Q:	What is my ATM withdrawal limit?
#3 A:	What is my ATM withdrawal limit?
#4 tokenized
#5 Q:	what is my atm withdrawal limit
#6 A:	what is my atm withdrawal limit
#7 spellcheck
#8 what is my atm withdrawal limit
#9 label:	correct, untouched


def create_result_from_string(item):
    split_item = [line for line in item.splitlines() if line != "" and line != "\'"]
    index = int(split_item[0][:-1])
    oQ = split_item[2].split("\t")[1]
    oA = split_item[3].split("\t")[1]
    tQ = split_item[5].split("\t")[1]
    tA = split_item[6].split("\t")[1]
    sQ = split_item[8]
    return Result(index,oQ,oA,tQ,tA,sQ)
    
resultStringFormat = "\n{}:\noriginal\nQ:\t{}\nA:\t{}\ntokenized\nQ:\t{}\nA:\t{}\nspellcheck\n{}\n"


'''
Read-only SpellCheck result
A class that wraps a named tuple
'''
class Result:
    def __init__(self, index, oQ, oA, tQ, tA, sQ):
        self.r = ResultTuple(index, oQ, oA, tQ, tA, sQ)
        self.field_dict = {k: self.r[self.r._fields.index(k)] for k in self.r._fields}
        
    
    def was_touched(self):
        return self.tokenizedQ != self.tokenizedA
    
    def was_correct(self):
        return self.tokenizedA != self.spellcheckedQ
    
    def correct_touched(self):
        return self.was_touched() and self.was_correct()
    
    def incorrect_touched(self):
        return self.was_touched() and not self.was_correct()
    
    def correct_untouched(self):
        return not self.was_touched() and self.was_correct()
    
    def incorrect_untouched(self):
        return not self.was_touched() and not self.was_correct()

    def __getattr__(self, attr):
        return self.field_dict[attr]
    
    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return resultStringFormat.format(self.r.index, self.r.originalQ, self.r.originalA, self.r.tokenizedQ, self.r.tokenizedA, self.r.spellcheckedQ)


if __name__ == "__main__":
    # utterance1 = "I want to watch a mavie"
    # stat_to_string(utterance1)
    #
    # print("\n")
    # utterance2 = "How much do i have in my caccount"
    # stat_to_string(utterance2)
    #
    # print("\n")
    # utterance2 = "How much do i have in my what's my numbr"
    # stat_to_string(utterance2)

    spellcheck_file = 'qa_pairs_combined.txt'

    qas = dict()
    with open(spellcheck_file, 'r') as file:
        i = 0
        last = None
        for line in file:
            if line[0] == 'Q':
                last = line[2:-1]
            else:
                qas[last] = line[2:-1]


    shouldbe_touched = 0
    shouldbe_untouched = 0

    shouldbe_touched_incorrect = 0
    shouldbe_touched_is_touched = 0
    shouldbe_untouched_is_untouched = 0
    shouldbe_untouched_incorrect = 0

    incorrect_examples_shouldbe_untouched = []
    incorrect_examples_shouldbe_touched = []

    correct_examples_shouldbe_touched= []
    correct_examples_shouldbe_untouched = []

    for i, (q, a) in enumerate(qas.items()):
        # if i == 3:
        #     break
        q_string, q_corrected = extractSpellCheck(q)
        a_string, _ = extractSpellCheck(a)
        r = Result(i, q, a, q_string, a_string, q_corrected)
        print(r)
        if q_string == a_string:
            shouldbe_untouched += 1
            # shoudl be untouched
            if q_corrected == a_string:
                # should be untouched, is untouched
                shouldbe_untouched_is_untouched += 1
                correct_examples_shouldbe_untouched.append(r)

            else:
                shouldbe_untouched_incorrect += 1
                incorrect_examples_shouldbe_untouched.append(r)
        else:
            shouldbe_touched += 1
            # should be touched
            if q_corrected == a_string:
                # is touched_and_correct
                shouldbe_touched_is_touched += 1
                correct_examples_shouldbe_touched.append(r)
            else:
                shouldbe_touched_incorrect += 1
                incorrect_examples_shouldbe_touched.append(r)

    with open('spellcheck_results_stored_precision_recall.txt', 'w') as file:
        file.write("touched\n")
        denom =  shouldbe_untouched_incorrect + shouldbe_touched_is_touched
        if denom == 0:
            precision = 0
        else:
            precision = shouldbe_touched_is_touched / (shouldbe_untouched_incorrect + shouldbe_touched_is_touched)
        file.write("precision:\t {}/{}, {}\n".format(shouldbe_touched_is_touched,
                                                     (shouldbe_untouched_incorrect + shouldbe_touched_is_touched),
                                                     precision))
        if shouldbe_touched:
            recall = 0
        else:
            recall = shouldbe_touched_is_touched / shouldbe_touched
        file.write('recall\t {}/{}, {}\n'.format(shouldbe_touched_is_touched, shouldbe_touched, recall))
        file.write("untouched\n")

        if (shouldbe_touched_incorrect + shouldbe_untouched_is_untouched) == 0:
            precision = 0
        else:
            precision = shouldbe_untouched_is_untouched / (shouldbe_touched_incorrect + shouldbe_untouched_is_untouched)
        file.write("precision:\t {}/{}, {}\n".format(shouldbe_untouched_is_untouched,
                                                     (shouldbe_touched_incorrect + shouldbe_untouched_is_untouched),
                                                     precision))
        if (shouldbe_untouched == 0):
            recall = 0
        else:
            recall = shouldbe_untouched_is_untouched / shouldbe_untouched
        file.write('recall\t {}/{}, {}\n'.format(shouldbe_untouched_is_untouched, shouldbe_untouched, recall))

    doubleline = "\n\n"
    cats = ["correct, untouched", "incorrect, touched", "correct, touched", "incorrect_untouched"]
    lists = [correct_examples_shouldbe_untouched, incorrect_examples_shouldbe_touched, correct_examples_shouldbe_touched, incorrect_examples_shouldbe_untouched]
    with open("spellcheck_log.txt", 'w') as file:
        for (cat, lit) in zip(cats, lists):
            for item in lit:
                file.write(str(item))
                file.write("label:\t{}".format(cat))
                file.write(doubleline)



    print('ok')