import pytest
from django.conf import settings
from django.urls import reverse, resolve

pytestmark = pytest.mark.django_db


def test_detail(user: settings.AUTH_USER_MODEL):
    assert (
        reverse("users:detail", kwargs={"username": user.username})
        == f"/users/{user.username}/"
    )
    assert resolve(f"/users/{user.username}/").view_name == "users:detail"


def test_update():
    assert reverse("users:edit") == "/users/edit/"
    assert resolve("/users/edit/").view_name == "users:edit"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"
