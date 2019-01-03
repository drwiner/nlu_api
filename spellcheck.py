
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


resultStringFormat = "\n{}:\noriginal\nQ:\t{}\nA:\t{}\ntokenized\nQ:\t{}\nA:\t{}\nspellcheck\n{}\n"

class Result:
    def __init__(self, index, oQ, oA, tQ, tA, sQ):
        self.r = ResultTuple(index, oQ, oA, tQ, tA, sQ)

    def __str__(self):
        r = self.r
        return resultStringFormat.format(r.index, r.originalQ, r.originalA, r.tokenizedQ, r.tokenizedA, r.spellcheckedQ)


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