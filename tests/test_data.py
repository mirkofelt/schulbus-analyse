from pathlib import Path

import pandas as pd
import pytest

from schulbus_analyse.data import SOLL_MIN, load, valid_trips

DATA = Path(__file__).parents[1] / "data" / "connections.csv"


@pytest.fixture
def df():
    return load(DATA)


@pytest.fixture
def valid(df):
    return valid_trips(df)


def test_load_row_count(df):
    assert len(df) == 66


def test_soll_correct():
    assert SOLL_MIN == 456  # 07:36


def test_versp_column_exists(df):
    assert "versp" in df.columns
    assert "versp_c" in df.columns


def test_versp_c_nonnegative(valid):
    assert (valid["versp_c"] >= 0).all()


def test_schnee_excluded(valid):
    for d in ["2026-01-15", "2026-01-26"]:
        assert pd.Timestamp(d) not in valid["Datum"].values


def test_valid_trip_count(valid):
    # 66 rows - 2 Schneetage (15.01, 26.01) - 1 Streik (kein Eintrag, aber 26.01 leer)
    assert len(valid) >= 50


def test_jan15_delay(df):
    jan15 = df[df["Datum"] == pd.Timestamp("2026-01-15")]
    assert len(jan15) == 1
    assert jan15.iloc[0]["versp"] > 30  # Schnee: deutlich verspätet
