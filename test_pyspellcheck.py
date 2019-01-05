
from kai_spellcheck import create_result_from_string

# pyspellcheck
from spellchecker import SpellChecker

spell = SpellChecker()

def get_unknown_words(word_list):
    return spell.unknown(word_list)


if __name__ == "__main__":
	spellcheck_log = 'spellcheck_log.txt'

	qas = dict()
	with open(spellcheck_log, 'r') as file:
		items = file.read().split("\n\n\n")
		qas = {i: create_result_from_string(item) for i, item in enumerate(items)}
	
	unfiltered_q = [word for result in qas.values() for word in result.tokenizedQ.split()]
	print(qas)
	unknown_words = get_unknown_words(unfiltered_q)
	print(unknown_words)
	
	points_of_contention = []
	all_results = []
	incorrect_touched = 0
	incorrect_untouched = 0
	correct_touched = 0
	correct_untouched = 0
	with open('pyspellcheck_results.txt', 'w') as outputfile:
		for result in qas.values():
			word_fixed = False
			incorrect_words = []
			new_result = []
			for word in result.tokenizedQ.split():
				spell_checked_word = spell.correction(word)
				
				if word != spell_checked_word:
					print(word, spell_checked_word)
					incorrect_words.append((word, spell_checked_word))
					word_fixed = True
					new_result.append(spell_checked_word)
					# break
				else:
					new_result.append(word)
					
			# if word_fixed:
			# 	points_of_contention.append((result, incorrect_words))
				
			spell_corrected_utterance = ' '.join(word for word in new_result).strip()
			# print(spell_corrected_utterance)
			correct = spell_corrected_utterance == result.tokenizedQ
			
			if result.was_touched() and correct:
				correct_touched += 1
			if not result.was_touched() and correct:
				correct_untouched += 1
			if result.was_touched() and not correct:
				incorrect_touched += 1
			if not result.was_touched() and not correct:
				incorrect_untouched +=1
				
		
		
		# how many of touched labels are correct
		recall_touched = (correct_touched / (incorrect_touched + correct_touched))
		# how many of untouched labels are correct
		recall_untouched = (correct_untouched / (incorrect_untouched + correct_untouched))
		# how many touched labels were recalled
		precision_touched = (correct_touched / (correct_touched + incorrect_untouched))
		# how many untouched labels were recalled
		precision_untouched = (correct_untouched / (correct_untouched + incorrect_touched))
		
		s1 = "precision touched:\t{}\t{}/{}".format(precision_touched, correct_touched, incorrect_untouched + correct_touched)
		s2 = "precision untouched:\t{}\t{}/{}".format(precision_untouched, correct_untouched, incorrect_touched + correct_untouched)
		s3 = "recall touched:\t{}\t{}/{}".format(recall_touched, correct_touched, correct_untouched + incorrect_untouched)
		s4 = "recall untouched:\t{}\t{}/{}".format(recall_untouched, correct_untouched, correct_untouched + incorrect_untouched)
		
		print(s1)
		print(s2)
		print(s3)
		print(s4)
			
		with open("pyspellcheck_results.txt", 'w') as file:
			file.write(s1 + "\n")
			file.write(s3 + "\n")
			file.write(s2 + "\n")
			file.write(s4 + "\n")
			
	# print(points_of_contention)
	
		
	# word_list_q = [word for word in qas.keys()]
	# get_unknown_words()