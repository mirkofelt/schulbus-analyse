from datetime import date

from schulbus_analyse.calendar import is_schultag, schultage


def test_weekend_no_schultag():
    assert not is_schultag(date(2026, 1, 17))  # Samstag
    assert not is_schultag(date(2026, 1, 18))  # Sonntag


def test_ferien_no_schultag():
    assert not is_schultag(date(2026, 2, 4))   # Winterferien


def test_feiertag_no_schultag():
    assert not is_schultag(date(2026, 5, 1))   # Tag der Arbeit


def test_brueckentag_no_schultag():
    assert not is_schultag(date(2026, 5, 15))  # Brückentag nach Himmelfahrt


def test_normaler_schultag():
    assert is_schultag(date(2026, 1, 19))      # Montag, kein Feiertag
    assert is_schultag(date(2026, 3, 2))


def test_schultage_count():
    days = schultage(date(2026, 1, 13), date(2026, 5, 22))
    assert len(days) == 76


def test_schultage_no_duplicates():
    days = schultage(date(2026, 1, 13), date(2026, 5, 22))
    assert len(days) == len(set(days))
