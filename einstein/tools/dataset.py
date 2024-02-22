import time
import random
import mathgenerator
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
    topics_list = mathgenerator.getGenList()

    def __init__(self, seed=None):
        # NOTE: Unfortunately, mathgenerator does not provide a way to seed the random number generator and get the same problem every time

        self.seed = seed
        self.rng = random.Random(seed)

    def random_problem(self, parse):
        if parse:
            parseable_list = [
                2, 7, 11, 15, 19, 21, 24, 27, 29, 30, 32, 33, 35, 36, 42, 45, 48, 49, 52, 59,
                60, 64, 66, 67, 68, 69, 70, 73, 76, 78, 81, 82, 83, 84, 85, 86, 87, 92, 94, 95,
                96, 97, 105, 108, 109, 111, 115, 122, 123,
            ]
            options = parseable_list
            choice = self.rng.choice((options))
            # TODO: When the solution contains the symbol x we should specify the x value and substitute it in the solution
            problem, solution = mathgenerator.genById(choice)
            _, subtopic, _, _, topic, _ = self.topics_list[choice]

            subs = {}
            # check if solution contains letters
            if "x" in solution:
                subs["x"] = 10
                bt.logging.warning(
                    "Coercing a symbolic expression to a numeric expression by substituting x=10"
                )

            # BUG: parse latex assumes that all letters are variables and so solutions like $No$ are interpreted as 'N * o'
            solution_numeric = parse_latex(
                str(solution).replace("$", "").strip()
            ).evalf(subs=subs)
            return {
                "problem": problem,
                "solution": solution_numeric,
                "solution_raw": solution,
                "topic": topic,
                "subtopic": subtopic,
            }
        else:
            options = mathgenerator.getGenList()
            choice = self.rng.choice(range(len(options)))
            problem, solution = mathgenerator.genById(choice)
            _, subtopic, _, _, topic, _ = self.topics_list[choice]
            return {
                "problem": problem,
                "solution": solution,
                "topic": topic,
                "subtopic": subtopic,
            }

    def next(self, parse=True):
        t0 = time.time()
        info = self.random_problem(parse)
        info["fetch_time"] = time.time() - t0
        return info
