"""SQL for the performance_reviews table."""

from typing import Optional

from db.connection import fetch_all

_SELECT_REVIEWS = """
    SELECT pr.id,
           pr.employee_id,
           e.employee_id AS employee_code,
           e.name        AS employee_name,
           pr.period_id,
           rp.name       AS period_name,
           pr.quality_rating,
           pr.delivery_rating,
           pr.teamwork_rating,
           pr.average_rating,
           pr.comments,
           pr.created_at
      FROM performance_reviews pr
      JOIN employees e       ON e.id  = pr.employee_id
      JOIN review_periods rp ON rp.id = pr.period_id
"""


def list_reviews(employee_id: Optional[int] = None, period_id: Optional[int] = None) -> list[dict]:
    clauses, params = [], []
    if employee_id is not None:
        clauses.append("pr.employee_id = %s")
        params.append(employee_id)
    if period_id is not None:
        clauses.append("pr.period_id = %s")
        params.append(period_id)

    sql = _SELECT_REVIEWS
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY pr.created_at DESC, pr.id DESC"
    return fetch_all(sql, params)
