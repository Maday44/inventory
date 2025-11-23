from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from storage.api_views import FoodViewSet, OtherViewSet, UserViewSet, FamViewSet
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r"Food items", FoodViewSet, basename="food-items")
router.register(r"Other items", OtherViewSet, basename="other-items")
router.register(r"Users", UserViewSet, basename="Users")
router.register(r"Families", FamViewSet, basename="Families")

urlpatterns = [
    path("", include("storage.urls")),  # Your app-specific views
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("datawizard/", include("data_wizard.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
