import inspect

def _getargspec(func):
    """Возвращаем ровно (args, varargs, varkw, defaults)."""
    full = inspect.getfullargspec(func)
    return (full.args, full.varargs, full.varkw, full.defaults)

inspect.getargspec = _getargspec

import re
import string
from collections import defaultdict, Counter
from docx import Document
import nltk
import pymorphy2

# При первом запуске, если ещё не скачали стоп-слова:
# nltk.download('stopwords')

from nltk.corpus import stopwords

morph = pymorphy2.MorphAnalyzer()

def load_docx_text(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def rake_extract(text, stop_words):
    sentences = re.split(r'[.!?]+\s*', text)
    phrases = []
    for sent in sentences:
        tokens = re.findall(r'\b\w+\b', sent.lower())
        phrase = []
        for w in tokens:
            if w in stop_words or w.isdigit() or len(w) == 1:
                if phrase:
                    phrases.append(phrase); phrase = []
            else:
                phrase.append(w)
        if phrase:
            phrases.append(phrase)

    freq = defaultdict(int)
    degree = defaultdict(int)
    for phrase in phrases:
        deg = len(phrase) - 1
        for word in phrase:
            freq[word] += 1
            degree[word] += deg
    for word in freq:
        degree[word] += freq[word]

    word_score = {w: degree[w] / freq[w] for w in freq}
    phrase_score = defaultdict(float)
    for phrase in phrases:
        score = sum(word_score[w] for w in phrase)
        phrase_score[" ".join(phrase)] += score

    return phrase_score, freq

def clean_punct(s: str) -> str:
    return s.translate(str.maketrans('', '', string.punctuation))

def lemmatize(word: str) -> str:
    return morph.parse(word)[0].normal_form

def get_keywords_and_topic(docx_path, top_n=10):
    # nltk.download('stopwords')
    text = load_docx_text(docx_path)
    custom = {"шаг","k","к","и","а","но","в","об","о","рисунок","её","ей"}
    stop_words = set(stopwords.words('russian')) | custom

    phrase_score, word_freq = rake_extract(text, stop_words)

    lemma_freq = defaultdict(int)
    for w, f in word_freq.items():
        lemma_freq[lemmatize(w)] += f

    top_words = Counter(lemma_freq).most_common(top_n)

    raw_topic, _ = max(phrase_score.items(), key=lambda x: x[1])
    tokens = re.findall(r'\b\w+\b', raw_topic.lower())
    lemma_topic = " ".join(lemmatize(t) for t in tokens)

    return top_words, lemma_topic

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python extract_keywords.py <путь_к_файлу.docx>")
        sys.exit(1)

    path = sys.argv[1]
    keywords, topic = get_keywords_and_topic(path, top_n=10)

    print("Тема документа:", topic)
    print("\nКлючевые слова и их частоты:")
    for word, freq in keywords:
        print(f"{word}: {freq}")
