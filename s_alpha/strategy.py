"""Small supervised strategy selector for requirement interpretation."""
import re
from .universal import interpret

def normalize(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.casefold()))

def predict(text, strategy):
    try:
        return interpret(normalize(text) if strategy == "normalized" else text)
    except ValueError:
        return None

def evaluate(examples, strategy):
    return sum(predict(text,strategy)==label for text,label in examples)

def train(examples):
    examples = list(examples)
    if not examples:
        raise ValueError("empty training set")
    return max(("raw","normalized"), key=lambda s:evaluate(examples,s))
