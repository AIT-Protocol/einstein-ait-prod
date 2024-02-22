
from prompting.tools import MockDataset, MathDataset

DATASETS = [
    # MockDataset,
    MathDataset,
]

MATH_CONTEXT = MathDataset(seed=123).next()

CONTEXTS = {
    MathDataset:  MATH_CONTEXT,
}


CONTEXT_FIELDS = {
    MathDataset: {"problem", "solution", 'topic', 'subtopic', "fetch_time", "solution_raw"},
}
