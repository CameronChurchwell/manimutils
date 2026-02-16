import pandas as pd
from manim import *
from .multi_table import MultiTable

class PandasTable(MultiTable):

    def __init__(self, df: pd.DataFrame, **kwargs):
        col_labels = np.array(df.columns.to_list()).T
        mask = np.concatenate([
            np.full((col_labels.shape[0], 1), False),
            col_labels[:, 1:] == col_labels[:, :-1]
        ], axis=1)
        col_labels = np.where(mask, '', col_labels)
        super().__init__(
            df.fillna('').astype(str).to_numpy(),
            col_labels=col_labels,
            row_labels=[
                Text(str(row)) for row in df.index.tolist()
            ],
            **kwargs
        )