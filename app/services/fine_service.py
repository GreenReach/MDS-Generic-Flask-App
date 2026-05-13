"""Fine calculation logic.

This module is intentionally tiny: it exists so the *policy* for fines
(grace period, tiered rates, currency rounding, ...) has one canonical
home and is trivial to unit-test in isolation. The model layer should
never do this arithmetic itself; the service layer should never inline
it either.
"""

from __future__ import annotations

from flask import current_app


def calculate_fine(days_overdue: int) -> float:
    """Return the fine for ``days_overdue`` full days past the due date.

    The per-day rate is read from the application config key
    ``FINE_PER_DAY`` (a float, defaults to ``0.50`` in development).

    Parameters
    ----------
    days_overdue:
        Number of full days the book is late. Values <= 0 produce no
        fine.

    Returns
    -------
    float
        Fine amount, rounded to two decimal places (currency-friendly).
    """
    if days_overdue <= 0:
        return 0.0
    rate: float = current_app.config["FINE_PER_DAY"]
    return round(days_overdue * rate, 2)
