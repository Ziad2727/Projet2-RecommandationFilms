from pathlib import Path
import pandas as pd

def get_project_paths():
    p = Path.cwd()
    while p != p.parent and not (p / "data").exists():
        p = p.parent
    data_raw = p / "data" / "raw"
    data_processed = p / "data" / "processed"
    return p, data_raw, data_processed

def load_imdb_light(filename="imdb_light.parquet"):
    _, _, data_processed = get_project_paths()
    return pd.read_parquet(data_processed / filename)


