"""
Lightweight Embeddings and Text Tokenizer Utility
"""
import re
import math
from collections import Counter

def tokenize(text):
    if not text:
        return []
    words = re.findall(r'\w+', str(text).lower())
    return [w for w in words if len(w) > 1]

def get_tf(tokens):
    tf = Counter(tokens)
    total = len(tokens) or 1
    return {w: count / total for w, count in tf.items()}

def cosine_similarity(tf1, tf2):
    intersection = set(tf1.keys()) & set(tf2.keys())
    numerator = sum([tf1[x] * tf2[x] for x in intersection])
    sum1 = sum([val ** 2 for val in tf1.values()])
    sum2 = sum([val ** 2 for val in tf2.values()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator:
        return 0.0
    return numerator / denominator
