import time
import random
import mathgenerator as mg
import bittensor as bt
from sympy.parsing.latex import parse_latex
from sympy import symbols, simplify, solve
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application


class MockDataset:
    def next(self):
        return {"text": "What is Einstein's Special Theory Of Relativity Equation?"}


def chunk(text, sep, n_chunks=None):
    # choose a random chunk from the article
    chunks = [chunk for chunk in text.split(sep) if chunk.strip()]
    # select a subsequence of paragraphs
    if n_chunks is None:
        n_chunks = random.randint(1, len(chunks))

    start_chunk = random.randint(0, len(chunks) - n_chunks)
    bt.logging.info(f"Choosing {n_chunks} chunks starting at index {start_chunk}.")

    return sep.join(chunks[start_chunk : start_chunk + n_chunks])


class MathDataset:
    def __init__(self, seed=None):
        self.seed = seed
        self.rng = random.Random(seed)

    def next(self):
        while True:
            t0 = time.time()
            info = mg.generate_context()
            info["fetch_time"] = time.time() - t0
            print(info)
            if info['reward_model'] == 'float':
                return info
