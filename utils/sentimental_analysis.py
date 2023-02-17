import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from spacy import displacy
from spacy.matcher import Matcher
from nltk import tokenize
import re

def subtree_matcher(doc):
    subjpass = 0

    for i, tok in enumerate(doc):
        # find dependency tag that contains the text "subjpass"
        if tok.dep_.find("subjpass") == True:
            subjpass = 1

    x = ''
    y = ''

    # if subjpass == 1 then sentence is passive
    if subjpass == 1:
        for i, tok in enumerate(doc):
            if tok.dep_.find("subjpass") == True:
                y = tok.lemma_

            if tok.dep_.endswith("obj") == True:
                x = tok.lemma_

    # if subjpass == 0 then sentence is not passive
    else:
        for i, tok in enumerate(doc):
            if tok.dep_.endswith("subj") == True:
                x = tok.lemma_

            if tok.dep_.endswith("obj") == True:
                y = tok.lemma_

    return x, y

question = "Is oak wood a suitable material for a nightstand base in hotel rooms?"

text = '''
 You obviously mean oak wood and not veneer - which is usually no. Oak, even if treated, will not survive the abuse caused by the frequent opening and closing of the drawers and doors. As a matter of fact, it's actually not advisable to do it yourself either - in case you don't want your bedstand to fall apart in a couple of weeks.

Even pine wood won't be able to cope with the treatment that it will get in hotel rooms - the constant opening of drawers and doors, combined with the temperature fluctuations (hot in the summer, cold in the winter) will not take kindly to this material. The other problem is that any traces of water on pine will cause the wood to swell.

What is usually used for such projects are some types of particle board. These can be easily stained, and depending on their thickness can provide a very solid surface on which to build furniture. But yes, it will not last too long as well, and you will have to regularly sand and stain the surface to keep it looking good.

'''

nlp = spacy.load('en_core_web_md')
nlp.add_pipe('spacytextblob')

textdoc = nlp(text)
sentence_list = tokenize.sent_tokenize(text)
quesdoc = nlp(question)
terms = subtree_matcher(quesdoc)

sentences_found = []

print()
for i in sentence_list:
    if(re.search(terms[1], i, re.IGNORECASE) or re.search(terms[0], i, re.IGNORECASE)):
        sentences_found.append(i)

for i in sentences_found:
    print(i, end=" ")
print('\n')

print(f'Polarity {textdoc._.blob.polarity}')
print(f'Assessments: {textdoc._.blob.sentiment_assessments.assessments}')
print()
print()
# doc._.blob.polarity                            # Polarity: -0.125
# doc._.blob.subjectivity                        # Subjectivity: 0.9
# doc._.blob.sentiment_assessments.assessments   # Assessments: [(['really', 'horrible'], -1.0, 1.0, None), (['worst', '!'], -1.0, 1.0, None), (['really', 'good'], 0.7, 0.6000000000000001, None), (['happy'], 0.8, 1.0, None)]
# doc._.blob.ngrams()           