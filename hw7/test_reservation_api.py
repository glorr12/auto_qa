import pytest
import requests

HOTEL_API_URL = "https://restful-booker.herokuapp.com"
ADMIN_LOGIN = "admin"
ADMIN_SECRET = "password123"


class ReservationClient:
    def __init__(self, root_url):
        self.root_url = root_url

    def make_reservation(self, reservation_body):
        return requests.post(f"{self.root_url}/booking", json=reservation_body)

    def patch_reservation(self, reservation_id, changes, session_token):
        request_headers = {
            "Cookie": f"token={session_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        return requests.patch(
            f"{self.root_url}/booking/{reservation_id}",
            json=changes,
            headers=request_headers,
        )

    def fetch_session_token(self, login, secret):
        credentials = {"username": login, "password": secret}
        auth_response = requests.post(f"{self.root_url}/auth", json=credentials)
        return auth_response.json().get("token")


def build_guest_data(first, last, price):
    return {
        "firstname": first,
        "lastname": last,
        "totalprice": price,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
    }


@pytest.fixture
def reservation_client():
    return ReservationClient(HOTEL_API_URL)


@pytest.fixture
def session_token(reservation_client):
    return reservation_client.fetch_session_token(ADMIN_LOGIN, ADMIN_SECRET)


def test_new_reservation_is_saved(reservation_client):
    guest_data = build_guest_data("Jim", "Brown", 111)
    result = reservation_client.make_reservation(guest_data)
    assert result.status_code == 200
    assert result.json()["booking"]["firstname"] == "Jim"


def test_reservation_name_can_be_patched(reservation_client, session_token):
    original_guest = build_guest_data("Test", "User", 100)
    new_reservation_id = reservation_client.make_reservation(original_guest).json()["bookingid"]
    name_change = {"firstname": "UpdatedName"}
    result = reservation_client.patch_reservation(new_reservation_id, name_change, session_token)
    assert result.status_code == 200
    assert result.json()["firstname"] == "UpdatedName"


def test_patch_rejected_with_bad_token(reservation_client):
    name_change = {"firstname": "Fail"}
    result = reservation_client.patch_reservation(999999, name_change, session_token="invalid_token")
    assert result.status_code == 403
