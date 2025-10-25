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
    path('add_food/', views.add_food, name='add_food'),
    path("choose_add_food/",views.choose_add_food,name="choose_add_food"),
    path('food/<slug:slug>/delete', views.food_item_delete, name='food-delete'),
    path('food/<slug:slug>/edit/', views.food_edit, name='food_edit'),
    
    # other items
    path('all_other_items', views.all_other, name='all_other_items'),
    path('other/<slug:slug>/', views.other_detail, name='other-detail'),
    path("choose_add_other/",views.choose_add_other,name="choose_add_other"),
    path('add_other_items/', views.add_other_items, name='add_other'),
    path('other/<slug:slug>/delete', views.other_item_delete, name='other-delete'),
    path('other/<slug:slug>/edit/', views.other_edit, name='other_edit'),
    
    #profile
    path("profile/", views.profile_detail, name="my_profile"),  # view your own
    path("profile/<int:user_id>/", views.profile_detail, name="profile_detail"), 
    path('profile/<int:id>/edit/', views.edit_profile, name='edit_profile'),
    
    #memebers
    path("family/members/", views.all_members, name="members"),
    path("family/edit/<int:member_id>/", views.edit_member_view, name="edit_member"),
    
    path('accounts/logout/', views.custom_logout, name='logout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
