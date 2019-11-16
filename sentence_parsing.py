from nltk.parse.corenlp import CoreNLPParser
from word2number import w2n

parser = CoreNLPParser()


def find_positive_sentences(node):
    candidates = list(node.subtrees(lambda t: t.label() == 'S'))
    sentences = []
    for candidate in candidates:
        exclude = False
        subtrees = list(candidate.subtrees())
        for subtree in subtrees:
            if subtree != candidate:
                if subtree.label() == 'S':
                    exclude = True
                break
        if not exclude:
            sentences.append(candidate)
    return sentences


def extract_condition_from_sentence(sentence):
    for parse_tree_candidate in parser.raw_parse(sentence):
        #print(parse_tree_candidate)
        data = {'valid_and_placed': 0, 'valid_on_invalid_places': 0}

        for node in parse_tree_candidate:
            found = False
            subsentences = find_positive_sentences(node)
            for subsentence  in subsentences:
                if subsentence is not None:
                    try:
                        np_clause = next(subsentence.subtrees(lambda t: t.label() == 'NP'))
                        number = w2n.word_to_num(next(np_clause.subtrees(lambda t: t.label() == 'CD'))[0])
                        vp_clause = next(subsentence.subtrees(lambda t: t.label() == 'VP'))
                        correct_clause = next(vp_clause.subtrees(lambda t: t.label() == 'ADJP' and 'correct' in t.leaves()))
                        is_valid = 'well' in correct_clause.leaves()
                        #print(number, is_valid)
                        data['valid_and_placed' if is_valid else 'valid_on_invalid_places'] = number
                        found = True
                    except StopIteration:
                        pass
            if found:
                return data

        return {'valid_and_placed': 0, 'valid_on_invalid_places': 0}


if __name__ == '__main__':
    sentences = [
        'One number is correct and well placed',
        'One number is correct but wrong placed',
        'One number is correct but wrong place',
        'Two numbers are correct but wrong placed',
        'Nothing is correct',
        'One number is correct but wrong placed',
        "One number is correct and well placed and two numbers are correct but wrong placed"
    ]

    for sentence in sentences:
        print(sentence, extract_condition_from_sentence(sentence))
