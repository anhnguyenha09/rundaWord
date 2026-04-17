import random


def build_quiz_words(vocabs, max_questions: int = 3, max_options: int = 4):
    """
    Build quiz questions from a list of Vocabulary-like objects
    that have `.id`, `.word_en`, `.word_vi`.
    """
    quiz_words = []
    if not vocabs or len(vocabs) < 2:
        return quiz_words

    sample = random.sample(vocabs, min(max_questions, len(vocabs)))
    for v in sample:
        wrong_pool = [x.word_vi for x in vocabs if x.id != v.id]
        wrong = random.sample(wrong_pool, min(max_options - 1, len(wrong_pool)))
        options = wrong + [v.word_vi]
        random.shuffle(options)
        quiz_words.append({"word": v.word_en, "correct": v.word_vi, "options": options})
    return quiz_words

