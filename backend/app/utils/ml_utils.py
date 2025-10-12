"""
Machine Learning Utilities - Mock implementations for sklearn functionality
Simple replacements to avoid heavy ML dependencies during development
"""

class TfidfVectorizer:
    """Simple mock for sklearn TfidfVectorizer"""

    def __init__(self, max_features=1000, stop_words='english'):
        self.max_features = max_features
        self.stop_words = stop_words

    def fit_transform(self, texts):
        # Mock implementation - returns simple similarity scores
        return [[0.5, 0.3, 0.2] for _ in texts]

def cosine_similarity(X, Y=None):
    """Simple mock for sklearn cosine_similarity"""
    # Returns mock similarity matrix
    if Y is None:
        n = len(X)
        return [[0.8 if i == j else 0.3 for j in range(n)] for i in range(n)]
    else:
        return [[0.6 for _ in Y] for _ in X]