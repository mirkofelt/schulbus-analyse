from pathlib import Path

import numpy as np
import pandas as pd

STOP = "Zeesen, Schule"
SOLL_MIN = 7 * 60 + 36  # 07:36


def _to_min(t) -> float:
    if pd.isna(t) or str(t).strip() in ("", "nan"):
        return np.nan
    parts = str(t).strip().split(":")
    return int(parts[0]) * 60 + int(parts[1])


def load(path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Datum"])
    df["ankunft_min"] = df[STOP].apply(_to_min)
    df["versp"] = df["ankunft_min"] - SOLL_MIN
    df["versp_c"] = df["versp"].clip(lower=0)
    return df


def valid_trips(df: pd.DataFrame) -> pd.DataFrame:
    from schulbus_analyse.calendar import SCHNEE
    import pandas as _pd

    exclude = {_pd.Timestamp(d) for d in SCHNEE}
    return df[~df["Datum"].isin(exclude)].dropna(subset=["ankunft_min"]).copy()
