import numpy as np
import pandas as pd


def create_column_names(f):
    return ['dim_' + str(dim_index) for dim_index in range(f)]


class CountryVectors:

    def __init__(self, ratings_matrix, f, random_state):
        random_state = np.random.RandomState(random_state)
        self.vectors = pd.DataFrame(
            random_state.randn(ratings_matrix.R_ui.shape[0], f),
            columns=create_column_names(f),
            index=ratings_matrix.R_ui.index
        )

class SongVectors:

    def __init__(self, ratings_matrix, f, random_state):
        random_state = np.random.RandomState(random_state)
        self.vectors = pd.DataFrame(
            random_state.randn(ratings_matrix.R_ui.shape[1], f),
            columns=create_column_names(f),
            index=ratings_matrix.R_ui.columns
        )
