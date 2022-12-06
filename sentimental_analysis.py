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

question = "Can a steel table leg be attached to a wooden table top?"

text = '''
Would you like to strengthen the table top? If the answer is yes, then it could be done. 
You would want to drill a hole through the table top and table leg using a larger drill bit than you will use. 
In the hole, slip a bolt that is longer than the leg. Fit the bolt into the leg and bolt the leg into the top.
Hold the leg in position and drill the hole, and then it is time to use the large bit. 
You can sand the bottom of the table top as well to conceal the hardware.
We hope you enjoy these tips and that you found these answers helpful. 
There are many more tips in the book, "Wood Working Ideas". 
Check out the book and share your comments with us.
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
# doc._.blob.polarity                            # Polarity: -0.125
# doc._.blob.subjectivity                        # Subjectivity: 0.9
# doc._.blob.sentiment_assessments.assessments   # Assessments: [(['really', 'horrible'], -1.0, 1.0, None), (['worst', '!'], -1.0, 1.0, None), (['really', 'good'], 0.7, 0.6000000000000001, None), (['happy'], 0.8, 1.0, None)]
# doc._.blob.ngrams()           