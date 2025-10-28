import manimutils
from manim import *
from tensorflow.python.summary.summary_iterator import summary_iterator
from typing import List, Optional
from pathlib import Path
import pandas as pd
from .pandas_table import PandasTable

def read_scalars(run_dir: Path, scalars: List[str]):
    data = []
    tags = set()
    for file in run_dir.rglob('events.out.tfevents.*'):
        for event in summary_iterator(str(file)):
            for value in event.summary.value:
                tags.add(value.tag)
                if value.tag in scalars:
                    data.append({
                        'step': event.step,
                        'scalar': value.tag,
                        'value': value.simple_value,
                    })
    if len(data) == 0:
        breakpoint()
    return pd.DataFrame(data)

def read_scalars_final(run_dir: Path, scalars: List[str]):
    df = read_scalars(run_dir, scalars)
    df = df.loc[df.groupby('scalar')['step'].idxmax()]
    # df = df.reset_index(drop=True)
    df = df.pivot(index='step', columns='scalar', values='value').reset_index()
    df.columns.name = None
    return df

def read_runs_scalars_final(runs_dir: Path, runs: List[str], scalars: List[str]):
    run_dfs = [] # dfs = DataFrames, not depth-first-search :)
    for run in runs:
        run_dir = runs_dir / run
        run_df = read_scalars_final(run_dir, scalars)
        run_df['run'] = run
        run_dfs.append(run_df)
    df = pd.concat(run_dfs, ignore_index=True)
    # columns_order = ['run'] + [col for col in df.columns if col != 'run']
    # df = df[columns_order]
    df = df.set_index('run')
    return df
    

class TensorBoardTable(PandasTable):

    def __init__(
        self,
        run_dir: Path,
        runs: List[str],
        scalars: List[str],
        sort_by: Optional[str] = None,
        ascending: Optional[bool] = False
    ):
        run_dir = Path(run_dir)
        df = read_runs_scalars_final(
            run_dir,
            runs,
            scalars,
        )

        if sort_by:
            df = df.sort_values(by=sort_by, ascending=ascending)

        df = df.round(3)

        super().__init__(df)