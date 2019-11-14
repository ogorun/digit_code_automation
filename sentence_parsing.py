import nltk
from word2number import w2n

def extract_condition_from_sentence(sentence):
    grammar = r"""
NUMBER_CLAUSE: {<CD><NN|NNS>}
VALIDATION: {<RB|JJ><VBD|VBN|NN|NNS>}
SingleCondition: {<NUMBER_CLAUSE>(<VBZ|VBP>)<JJ><CC><VALIDATION>}
NothingCondition: {<NN><VBZ><JJ>}
"""
    parser = nltk.RegexpParser(grammar)

    sent_pos = nltk.pos_tag(sentence.split())
    #print(sent_pos)
    res = parser.parse(sent_pos)
    #print(res)
    data = {'valid_and_placed': 0, 'valid_on_invalid_places': 0}
    for subtree in res.subtrees():
        if subtree.label() == 'NothingCondition':
            #print('Nothing', {'valid_and_placed': 0, 'valid_on_invalid_places': 0})
            pass
        elif subtree.label() == 'SingleCondition':
            #print('Single', subtree)
            assert subtree[0].label() == 'NUMBER_CLAUSE'
            assert subtree[0][0][1] == 'CD'
            number = w2n.word_to_num(subtree[0][0][0])
            assert subtree[-1].label() == 'VALIDATION'
            if subtree[-1][0][0] == 'well':
                key = 'valid_and_placed'
            else:
                key = 'valid_on_invalid_places'
            data[key] = number

    return data


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
