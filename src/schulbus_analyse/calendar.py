from datetime import date, timedelta

FERIEN = [
    (date(2025, 12, 22), date(2026, 1, 2)),
    (date(2026, 2, 2), date(2026, 2, 7)),
    (date(2026, 3, 28), date(2026, 4, 11)),
    (date(2026, 5, 25), date(2026, 6, 6)),
]

FEIERTAGE = [
    date(2026, 1, 1),
    date(2026, 4, 3),
    date(2026, 4, 6),
    date(2026, 5, 1),
    date(2026, 5, 14),
    date(2026, 5, 25),
]

BRUECKENTAGE = [date(2026, 5, 15)]

STREIK = {date(2026, 2, 27)}
SCHNEE = {
    date(2026, 1, 15),
    date(2026, 1, 26),
}  # 15.01 Schneechaos (sehr spät aber aufgezeichnet), 26.01 kein Service
SKRIPT = {
    date(2026, 3, 10),
    date(2026, 3, 19),
    date(2026, 3, 26),
    date(2026, 4, 14),
    date(2026, 4, 17),
    date(2026, 4, 30),
    date(2026, 5, 11),
}


def is_ferien(d: date) -> bool:
    return any(s <= d <= e for s, e in FERIEN)


def is_schultag(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    if is_ferien(d):
        return False
    if d in FEIERTAGE or d in BRUECKENTAGE:
        return False
    return True


def schultage(start: date, end: date) -> list[date]:
    return [
        start + timedelta(n)
        for n in range((end - start).days + 1)
        if is_schultag(start + timedelta(n))
    ]
