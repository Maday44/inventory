# main app urls

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from storage.api_views import FoodViewSet, OtherViewSet, UserViewSet, FamViewSet

router = DefaultRouter()
router.register(r'Food items', FoodViewSet, basename='Food')
router.register(r'Other items', OtherViewSet, basename='Other Items')
router.register(r'Users', UserViewSet, basename='Users')
router.register(r'Families', FamViewSet, basename='Families')

urlpatterns = [
    path('', include(router.urls)),  # DO NOT prefix with 'api' here
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(router.urls)),

]

