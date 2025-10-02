from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# this will be my main URL 
urlpatterns = [
    # Your app-specific views
    # Example: path('', views.home, name='home'),
    #path('food-items/', views.view_all_items, name='view_all_items'),
    path('', views.view_all_items, name='view_all_items'),
    path('all_food', views.all_food, name='all_food'),
    path('add_food', views.add_food_item, name='add_food_item'),
    path('edit_food', views.edit_item_quantity, name='edit_item_quantity'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
