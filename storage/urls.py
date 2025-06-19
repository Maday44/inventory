from django.urls import path, include
from rest_framework.routers import DefaultRouter
from storage.api_views import FoodViewSet, OtherViewSet, UserViewSet, FamViewSet

router = DefaultRouter()
router.register(r'Food', FoodViewSet, basename='Food Items')
router.register(r'Other', OtherViewSet, basename='Other Items')
router.register(r'Users', UserViewSet, basename='Users')
router.register(r'Family', FamViewSet, basename='Families')

urlpatterns = [
    # API ROUTES
    path('api/', include(router.urls)),

    # Optionally, if you want to log in to the browsable API
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
