import pandas as pd


def monthly_stats(valid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m in sorted(valid["Datum"].dt.month.unique()):
        mv = valid[valid["Datum"].dt.month == m]
        late = mv[mv["versp"] > 0]["versp"]
        rows.append(
            {
                "monat": m,
                "n": len(mv),
                "n_late": int((mv["versp"] > 0).sum()),
                "mean_c": round(mv["versp_c"].mean(), 1),
                "median_late": round(late.median(), 1) if len(late) else 0.0,
                "mean_late": round(late.mean(), 1) if len(late) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def weekday_stats(valid: pd.DataFrame) -> dict[int, list]:
    return {i: valid[valid["Datum"].dt.dayofweek == i]["versp_c"].tolist() for i in range(5)}


def overall_stats(valid: pd.DataFrame) -> dict:
    late = valid[valid["versp"] > 0]["versp"]
    return {
        "n_total": len(valid),
        "n_late": int((valid["versp"] > 0).sum()),
        "pct_punctual": round(100 * (len(valid) - int((valid["versp"] > 0).sum())) / len(valid), 1),
        "median_late": round(late.median(), 1) if len(late) else 0.0,
        "mean_late": round(late.mean(), 1) if len(late) else 0.0,
    }
