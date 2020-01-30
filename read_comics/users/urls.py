from django.urls import path

from read_comics.users.views import (
    user_redirect_view,
    user_edit_view,
    user_detail_view,
    user_change_photo_view,
    user_delete_photo_view,
    user_send_email_confirmation_view
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("edit/", view=user_edit_view, name="edit"),
    path("change_photo/", view=user_change_photo_view, name="change_photo"),
    path("delete_photo/", view=user_delete_photo_view, name="delete_photo"),
    path("send_email_confirmation", view=user_send_email_confirmation_view, name="send_email_confirmation"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
