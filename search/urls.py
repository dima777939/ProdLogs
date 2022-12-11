from django.urls import path
from . import views

app_name = "search"

urlpatterns = [
    path("", views.BaseSearchView.as_view(), name="mane_search"),
    path("advanced/", views.AdvancedSearchListView.as_view(), name="advanced_search"),
]
