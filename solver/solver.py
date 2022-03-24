import logging

import numpy as np
from tqdm import tqdm

from solver.config import Threshold


class Solver:
    def __init__(self, words_to_hit: list, words_to_avoid: list, embeddings: dict, n: int, threshold: float):
        """General Codenames Solver Class

        :param words_to_hit:
        :param words_to_avoid:
        :param embeddings:
        :param n:
        :param strategy: Either risky, moderate, conservative
        """
        self.words_to_hit = words_to_hit
        self.words_to_avoid = words_to_avoid
        self.embeddings = embeddings
        self.threshold = threshold
        self.n = n

    def solve(self, algorithm) -> list:
        """Takes algorithm object and gives prediction for best clues to link your words and avoid words that are not
        yours.

        :param algorithm: A solver.algorithm object that contains and solve method.
        :return: List of self.n Guess objects.
        """
        return algorithm(words_to_hit=self.words_to_hit,
                         embeddings=self.embeddings,
                         words_to_avoid=self.words_to_avoid,
                         n=self.n,
                         threshold=self.threshold
                         ).solve()


class SolverBuilder:
    def __init__(self, words_to_hit: list, words_to_avoid: list, embedding_path: str, n: int = 5, strategy: str = 'moderate'):
        self.words_to_hit = words_to_hit
        self.words_to_avoid = words_to_avoid
        self.embedding_path = embedding_path
        self.n = n
        self.threshold = getattr(Threshold, strategy)
        self.logger = logging.getLogger(__name__)

    def _persist_embeddings(self):
        raise NotImplementedError

    def build(self) -> Solver:
        embeddings = self._persist_embeddings()
        return Solver(words_to_hit=self.words_to_hit,
                      words_to_avoid=self.words_to_avoid,
                      embeddings=embeddings,
                      threshold=self.threshold,
                      n=self.n)


class GloveSolver(SolverBuilder):
    def __init__(self, words_to_hit: list, words_to_avoid: list, embedding_path: str, n: int, strategy: str):
        super().__init__(words_to_hit, words_to_avoid, embedding_path, n, strategy)
        self.logger = logging.getLogger(__name__)

    def _persist_embeddings(self) -> dict:
        self.logger.info("Loading GloVe embeddings...")
        embeddings = {}
        with open(self.embedding_path, "r") as file:
            for line in tqdm(file):
                split_line = line.split()
                word = split_line[0]
                embedding = np.array(split_line[1:], dtype=np.float64)
                embeddings[word] = embedding
        self.logger.info("GloVe embeddings loaded.")
        return embeddings


class AdversarialPostSpecSolver(SolverBuilder):
    def __init__(self, words_to_hit: list, words_to_avoid: list, embedding_path: str, n: int, strategy: str):
        # See https://github.com/cambridgeltl/adversarial-postspec
        super().__init__(words_to_hit, words_to_avoid, embedding_path, n, strategy)
        self.logger = logging.getLogger(__name__)

    def _persist_embeddings(self) -> dict:
        self.logger.info("Loading PostSpec embeddings...")
        embeddings = {}
        with open(self.embedding_path, "r") as file:
            for line in tqdm(file):
                split_line = line.split()
                word = split_line[0].split('_')
                if word[0] == 'en':
                    word = word[1]
                    embedding = np.array(split_line[1:], dtype=np.float64)
                    embeddings[word] = embedding
        self.logger.info("PostSpec embeddings loaded.")
        return embeddings
