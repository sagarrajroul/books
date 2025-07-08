from django.urls import path
from .views import BookFilterAPI

urlpatterns = [
    path("filter", BookFilterAPI.as_view(), name="books filter api")
]
