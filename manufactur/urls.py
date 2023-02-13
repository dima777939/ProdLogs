from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "manufactur"

urlpatterns = [
    path("", views.MainListView.as_view(), name="manufacture"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path(
        "logout",
        auth_views.LogoutView.as_view(template_name="manufactur/user/logout.html"),
        name="logout",
    ),
    path("users/", views.UserListView.as_view(), name="list_users"),
    path("user/<int:team>/", views.UserListView.as_view(), name="team_list_user"),
    path("user/follow/", views.UserFollowView.as_view(), name="user_follow"),
    path("user/<str:username>", views.UserDetailView.as_view(), name="user_detail"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("register/success/", views.UserRegisterView.as_view(), name="reg-done"),
]
