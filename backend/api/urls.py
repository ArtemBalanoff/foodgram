from rest_framework.routers import DefaultRouter
from django.urls import include, path

router_v1 = DefaultRouter()
router_v1.register()
urls_v1 = []



urlpatterns = [
    path('', include(urls_v1))
]
