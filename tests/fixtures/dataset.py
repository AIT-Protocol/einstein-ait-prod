
from einstein.tools.datasets import MathDataset, MockDataset

DATASETS = [
    MockDataset,
    MathDataset,
]


MOCK_CONTEXT = MockDataset().next()
MATH_CONTEXT = MathDataset(seed=123).next()

CONTEXTS = {
    MockDataset: MOCK_CONTEXT,
    MathDataset:  MATH_CONTEXT,
}

CONTEXT_FIELDS = {
    'title': str,
    'topic': str,
    'subtopic': str,
    'content': str,
    'internal_links': list,
    'external_links': list,
    'source': str,
    'tags': list,
    'extra': dict,
    'stats': dict,
}