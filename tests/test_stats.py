from pathlib import Path

import pytest

from schulbus_analyse.data import load, valid_trips
from schulbus_analyse.stats import monthly_stats, overall_stats, weekday_stats

DATA = Path(__file__).parents[1] / "data" / "connections.csv"


@pytest.fixture
def valid():
    return valid_trips(load(DATA))


def test_overall_n_total(valid):
    ov = overall_stats(valid)
    assert ov["n_total"] > 50


def test_overall_pct_range(valid):
    ov = overall_stats(valid)
    assert 0 < ov["pct_punctual"] < 100


def test_overall_median_positive(valid):
    ov = overall_stats(valid)
    assert ov["median_late"] > 0


def test_monthly_stats_columns(valid):
    ms = monthly_stats(valid)
    assert set(ms.columns) >= {"monat", "n", "n_late", "mean_c"}


def test_monthly_feb_mean(valid):
    ms = monthly_stats(valid)
    feb = ms[ms["monat"] == 2].iloc[0]
    # Feb mean of clamped values should be around 2 min
    assert 1.0 <= feb["mean_c"] <= 4.0


def test_monthly_mean_c_nonnegative(valid):
    ms = monthly_stats(valid)
    assert (ms["mean_c"] >= 0).all()


def test_weekday_stats_five_days(valid):
    ws = weekday_stats(valid)
    assert len(ws) == 5
    assert all(isinstance(v, list) for v in ws.values())
