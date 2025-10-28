import pandas as pd
from manim import *

class PandasTable(Table):

    def __init__(self, df: pd.DataFrame):
        super().__init__(
            df.astype(str).to_numpy(),
            col_labels=[
                Text(col) for col in df.columns.tolist()
            ],
            row_labels=[
                Text(row) for row in df.index.tolist()
            ]
        )