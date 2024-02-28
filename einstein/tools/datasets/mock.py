from .base import Dataset
from ..selector import Selector

class MockDataset(Dataset):

    def get(self, name, exclude=None, selector=None):
        mathematical_concepts = {
            'Quantum Computing': 'Quantum computing utilizes principles of quantum mechanics to process information in ways that classical computers cannot. It involves complex mathematical concepts such as qubits, superposition, and entanglement.',
            'Quantum Mechanics': 'A fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles, featuring mathematical frameworks like Schrödinger equation.',
            'Linear Algebra': 'Essential for understanding quantum computing, linear algebra involves the study of vectors, vector spaces, linear mappings, and systems of linear equations.',
            'Quantum Algorithms': 'Algorithms that run on a quantum computer, utilizing quantum phenomena to achieve significant speedups for certain computational problems, such as Shor’s algorithm for integer factorization.'
        }

        return {
            'title': name,
            'topic': 'Quantum Computing',
            'subtopic': 'mathematical_foundations',
            'content': mathematical_concepts.get(name, f'{name} is an important concept in quantum computing and its mathematical underpinnings.'),
            'internal_links': ['Quantum_mechanics', 'Linear_algebra', 'Quantum_algorithms', 'Quantum_entanglement'],
            'external_links': ['Dirac', 'Schrodinger', 'Turing', 'Grover'],
            "tags": ["quantum_computing", "mathematics", "algorithms", "entanglement"],
            'source': 'Mockpedia',
            'extra': {'key_concept': 'Superposition and entanglement are key concepts in quantum computing, enabling new computational capabilities.'},
        }

    def search(self, name, exclude=None, selector=None):
        return self.get(name)

    def random(self, name='Quantum Computing', exclude=None, selector=None):
        return self.get(name)
