
from nlu_api import NluApi

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

    for q, a in qas.items():
        q_string, q_corrected = extractSpellCheck(q)
        a_string, _ = extractSpellCheck(a)
        if q_string == a_string:
            shouldbe_untouched += 1
            # shoudl be untouched
            if q_corrected == a_string:
                # should be untouched, is untouched
                shouldbe_untouched_is_untouched += 1
            else:
                shouldbe_untouched_incorrect += 1
                incorrect_examples_shouldbe_untouched.append((q_corrected, a_string))
        else:
            shouldbe_touched += 1
            # should be touched
            if q_corrected == a_string:
                # is touched_and_correct
                shouldbe_touched_is_touched += 1
            else:
                shouldbe_touched_incorrect += 1
                incorrect_examples_shouldbe_touched.append((q_corrected,a_string))


    with open('spellcheck_results_stored_2.txt', 'w') as file:
        file.write("touched\n")
        precision = shouldbe_touched_is_touched / (shouldbe_untouched_incorrect + shouldbe_touched_is_touched)
        file.write("precision:\t {}/{}, {}\n".format(shouldbe_touched_is_touched,
                                                     (shouldbe_untouched_incorrect + shouldbe_touched_is_touched),
                                                     precision))
        recall = shouldbe_touched_is_touched / shouldbe_touched
        file.write('recall\t {}/{}, {}\n'.format(shouldbe_touched_is_touched, shouldbe_touched, recall))

        file.write("untouched\n")
        precision = shouldbe_untouched_is_untouched / (shouldbe_touched_incorrect + shouldbe_untouched_is_untouched)
        file.write("precision:\t {}/{}, {}\n".format(shouldbe_untouched_is_untouched,
                                                     (shouldbe_touched_incorrect + shouldbe_untouched_is_untouched),
                                                     precision))
        recall = shouldbe_untouched_is_untouched / shouldbe_untouched
        file.write('recall\t {}/{}, {}\n'.format(shouldbe_untouched_is_untouched, shouldbe_untouched, recall))

        print("\n\n")

        print("incorrect_examples_shouldbe_touched\n\n")
        file.write(str(incorrect_examples_shouldbe_touched))

        print("\n\nincorrect_examples_shouldbe_untouched\n\n")
        file.write(str(incorrect_examples_shouldbe_untouched))


    print('ok')