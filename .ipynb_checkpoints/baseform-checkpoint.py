from nltk.corpus import wordnet
import nltk

nltk.download('wordnet')

def lemma(lemmatizer, word):
    return lemmatizer.lemmatize(word.lower(), pos=wordnet.VERB)
def is_base_form_name(lemmatizer, word, base):
    return lemma(lemmatizer, word) == base
