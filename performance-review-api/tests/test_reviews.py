"""Tests for GET /api/reviews. Requires a reachable PostgreSQL database (see .env)."""

import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from db.connection import connection
from main import app

client = TestClient(app)
UNKNOWN_ID = 999_999_999


@pytest.fixture(scope="module")
def seed():
    """Insert 2 employees, 2 periods and 3 reviews; delete them afterwards."""
    tag = uuid.uuid4().hex[:6].upper()
    with connection() as conn:
        emp = [
            conn.execute(
                "INSERT INTO employees (employee_id, name, department, email, status) "
                "VALUES (%s, %s, 'Engineering', %s, 'Active') RETURNING id",
                (f"T{tag}{n}", f"Test Employee {n}", f"test{n}.{tag}@example.com"),
            ).fetchone()["id"]
            for n in (1, 2)
        ]
        per = [
            conn.execute(
                "INSERT INTO review_periods (name, start_date, end_date, status) "
                "VALUES (%s, %s, %s, 'Open') RETURNING id",
                (f"Test {tag} {name}", start, end),
            ).fetchone()["id"]
            for name, start, end in (("H1", "2026-01-01", "2026-06-30"), ("H2", "2026-07-01", "2026-12-31"))
        ]
        reviews = {}
        for key, e, p, ratings, created in (
            ("e1p1", emp[0], per[0], (4, 5, 4), "2026-07-05 11:00:00"),
            ("e1p2", emp[0], per[1], (3, 4, 4), "2026-10-25 09:30:00"),
            ("e2p1", emp[1], per[0], (5, 5, 5), "2026-08-01 08:00:00"),
        ):
            reviews[key] = conn.execute(
                "INSERT INTO performance_reviews "
                "(employee_id, period_id, quality_rating, delivery_rating, teamwork_rating, comments, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (e, p, *ratings, f"Test review {key}", created),
            ).fetchone()["id"]

    yield {"tag": tag, "emp": emp, "per": per, "reviews": reviews}

    with connection() as conn:
        conn.execute("DELETE FROM performance_reviews WHERE id = ANY(%s)", (list(reviews.values()),))
        conn.execute("DELETE FROM review_periods WHERE id = ANY(%s)", (per,))
        conn.execute("DELETE FROM employees WHERE id = ANY(%s)", (emp,))


def _ids(response):
    return [r["id"] for r in response.json()]


def _assert_sorted(rows):
    keys = [(datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")), r["id"]) for r in rows]
    assert keys == sorted(keys, reverse=True)


def test_no_filters_returns_all_reviews_newest_first(seed):
    response = client.get("/api/reviews")
    assert response.status_code == 200
    ids = _ids(response)
    r = seed["reviews"]
    assert {r["e1p1"], r["e1p2"], r["e2p1"]} <= set(ids)
    assert ids.index(r["e1p2"]) < ids.index(r["e2p1"]) < ids.index(r["e1p1"])
    _assert_sorted(response.json())


def test_filter_by_employee_id(seed):
    response = client.get("/api/reviews", params={"employee_id": seed["emp"][0]})
    assert response.status_code == 200
    assert _ids(response) == [seed["reviews"]["e1p2"], seed["reviews"]["e1p1"]]
    assert all(row["employee_id"] == seed["emp"][0] for row in response.json())


def test_filter_by_period_id(seed):
    response = client.get("/api/reviews", params={"period_id": seed["per"][0]})
    assert response.status_code == 200
    assert _ids(response) == [seed["reviews"]["e2p1"], seed["reviews"]["e1p1"]]


def test_filter_by_employee_and_period(seed):
    response = client.get("/api/reviews", params={"employee_id": seed["emp"][0], "period_id": seed["per"][1]})
    assert response.status_code == 200
    assert _ids(response) == [seed["reviews"]["e1p2"]]


@pytest.mark.parametrize("param", ["employee_id", "period_id"])
def test_unknown_id_returns_empty_list(seed, param):
    response = client.get("/api/reviews", params={param: UNKNOWN_ID})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("param", ["employee_id", "period_id"])
def test_non_integer_filter_returns_422(param):
    response = client.get("/api/reviews", params={param: "abc"})
    assert response.status_code == 422
    issue = response.json()["detail"][0]
    assert issue["loc"] == ["query", param]
    assert issue["type"] == "int_parsing"
    assert issue["msg"].startswith("Input should be a valid integer")


@pytest.mark.parametrize("value", ["0", "-1"])
def test_filter_below_one_returns_422(value):
    response = client.get("/api/reviews", params={"employee_id": value})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than_equal"


def test_response_values(seed):
    response = client.get("/api/reviews", params={"employee_id": seed["emp"][0], "period_id": seed["per"][0]})
    [row] = response.json()
    assert row == {
        "id": seed["reviews"]["e1p1"],
        "employee_id": seed["emp"][0],
        "employee_code": f"T{seed['tag']}1",
        "employee_name": "Test Employee 1",
        "period_id": seed["per"][0],
        "period_name": f"Test {seed['tag']} H1",
        "quality_rating": 4,
        "delivery_rating": 5,
        "teamwork_rating": 4,
        "average_rating": 4.33,
        "comments": "Test review e1p1",
        "status": "Completed",
        "created_at": "2026-07-05T11:00:00Z",
    }
    assert isinstance(row["average_rating"], float)


def test_openapi_documents_review_contract():
    schema = client.get("/openapi.json").json()
    op = schema["paths"]["/api/reviews"]["get"]
    assert op["responses"]["200"]["content"]["application/json"]["schema"]["items"]["$ref"].endswith("/Review")
    assert {p["name"] for p in op["parameters"]} == {"employee_id", "period_id"}
