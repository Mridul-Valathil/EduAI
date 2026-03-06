# import numpy as np


# def cosine_similarity(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# def calculate_importance(pyq_embeddings, chunk_embeddings, threshold=0.6):
#     """
#     For each PYQ embedding:
#         Find best matching textbook chunk.
#         If similarity > threshold → increment chunk score.
#     """

#     chunk_scores = [0] * len(chunk_embeddings)

#     for pyq_vec in pyq_embeddings:

#         similarities = [
#             cosine_similarity(pyq_vec, chunk_vec)
#             for chunk_vec in chunk_embeddings
#         ]

#         best_index = int(np.argmax(similarities))

#         if similarities[best_index] > threshold:
#             chunk_scores[best_index] += 1

#     return chunk_scores


# def classify_importance(chunk_scores):
#     """
#     Convert raw frequency scores into HIGH / MEDIUM / LOW
#     """

#     importance_labels = []

#     for score in chunk_scores:
#         if score >= 3:
#             importance_labels.append("HIGH")
#         elif score == 2:
#             importance_labels.append("MEDIUM")
#         else:
#             importance_labels.append("LOW")

#     return importance_labels

import numpy as np


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )


def calculate_chunk_scores(pyq_embeddings, chunk_embeddings, threshold=0.6):
    """
    For each PYQ question:
        Find most similar textbook chunk.
        If similarity > threshold → increment that chunk score.
    """

    chunk_scores = [0] * len(chunk_embeddings)

    for pyq_vec in pyq_embeddings:

        similarities = [
            cosine_similarity(pyq_vec, chunk_vec)
            for chunk_vec in chunk_embeddings
        ]

        best_index = int(np.argmax(similarities))
        best_score = similarities[best_index]

        if best_score > threshold:
            chunk_scores[best_index] += 1

    return chunk_scores


def classify_importance(chunk_scores):
    """
    Convert frequency into HIGH / MEDIUM / LOW labels.
    """

    importance_labels = []

    for score in chunk_scores:
        if score >= 3:
            importance_labels.append("HIGH")
        elif score == 2:
            importance_labels.append("MEDIUM")
        else:
            importance_labels.append("LOW")

    return importance_labels