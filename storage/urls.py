from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

# this will be my main URL 
urlpatterns = [
    # Your app-specific views
    # Example: path('', views.home, name='home'),
    #path('food-items/', views.view_all_items, name='view_all_items'),
    path('', views.view_all_items, name='view_all_items'),
    
    #food
    path('all_food_items', views.all_food, name='all_food'),
    path('food/<slug:slug>/', views.food_detail, name='food-detail'),
    path('add_food', views.add_food_item, name='add_food_item'),
    path('edit_food', views.edit_item_quantity, name='edit_item_quantity'),
    
    # other items
    path('all_other_items', views.all_other, name='all_other_items'),
    path('other/<slug:slug>/', views.other_detail, name='other-detail'),
    
    #profile
    path("profile/", views.profile_detail, name="my_profile"),  # view your own
    path("profile/<int:user_id>/", views.profile_detail, name="profile_detail"), 
    path('profile/<int:id>/edit/', views.edit_profile, name='edit_profile'),
    
    path('accounts/logout/', views.custom_logout, name='logout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
