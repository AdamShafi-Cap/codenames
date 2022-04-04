import logging
import os
import random

from game.wordlist import WordListBuilder
from solver.algorithms import NearestNeighborSum, BestAverageAngle
from solver.solver import PostSpecSolver, GloveSolver, WordNetSolver, StaticBertSolver


def initialise_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(message)8s')
    return logger


def run_glove_solver(algo, s):
    glove_embedding_path = os.path.join("..", "data", "word_embeddings", "glove", "glove.6B.300d.txt")
    glove_solver = GloveSolver(**CONFIG, embedding_path=glove_embedding_path, strategy=s).build()
    return glove_solver.solve(algo)


def run_postspec_solver(algo, s):
    p_path = ["..", "data", "word_embeddings", "post-specialized embeddings", "postspec", "glove_postspec.txt"]
    postspec_embedding_path = os.path.join(*p_path)
    postspec_solver = PostSpecSolver(**CONFIG, embedding_path=postspec_embedding_path, strategy=s).build()
    return postspec_solver.solve(algo)


def run_wordnet_solver(algo, s):
    w_path = ["..", "data", "word_embeddings", "wordnetemb", "embedding_cleaned.txt"]
    wordnet_embedding_path = os.path.join(*w_path)
    wordnet_solver = WordNetSolver(**CONFIG, embedding_path=wordnet_embedding_path, strategy=s).build()
    return wordnet_solver.solve(algo)


def run_bert_solver(algo, s):
    b_path = ["..", "data", "word_embeddings", "bert", "embedding.txt"]
    bert_embedding_path = os.path.join(*b_path)
    bert_solver = StaticBertSolver(**CONFIG, embedding_path=bert_embedding_path, strategy=s).build()
    return bert_solver.solve(algo)


def get_words(words):
    random.shuffle(words)
    negative = words[20:]
    positive = words[:7]
    return positive, negative


def log_solutions(solutions):
    dash = '-' * 80
    formatting = '{:<20s}{:<30s}{:<40}'
    for i, s in enumerate(solutions):
        if i == 0:
            LOGGER.info(dash)
            LOGGER.info(formatting.format("Clue", "Score", "Linked Words"))
            LOGGER.info(dash)
        else:
            LOGGER.info(formatting.format(s.clue, str(round(s.score, 3)), ', '.join(s.linked_words)))


if __name__ == "__main__":
    LOGGER = initialise_logger()
    strategy = 'moderate'
    n = 10
    algorithms = [NearestNeighborSum, BestAverageAngle]

    path_to_word_list = os.path.join("..", "data", "wordlist-eng.txt")
    wordlist = WordListBuilder(path_to_word_list).build().wordlist
    words_to_hit, words_to_avoid = get_words(wordlist)

    CONFIG = {"words_to_hit": words_to_hit, "n": n}

    if CONFIG.get("words_to_avoid"):
        LOGGER.info(f"Words to link: {', '.join(words_to_hit)}\nWords to avoid: {', '.join(words_to_avoid)}")
    else:
        LOGGER.info(f"Words to link: {', '.join(words_to_hit)}\n")

    funcs = [run_glove_solver, run_postspec_solver, run_wordnet_solver, run_bert_solver]
    for func in funcs:
        for algorithm in algorithms:
            log_solutions(func(algorithm, strategy))
