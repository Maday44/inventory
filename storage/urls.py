from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

# this will be my main URL
urlpatterns = [
    # accounts
    path("", views.view_all_items, name="view_all_items"),
    path("login/", views.login, name="logins"),
    path("logout/", views.logout, name="logouts"),
    path("callback/", views.callback, name="callback"),
    path("no_account/", views.no_account, name="no_account"),
    # new user to join
    path("family/create/", views.create_family, name="create_family"),
    path(
        "family/invite/<int:family_id>/", views.generate_invite, name="generate_invite"
    ),
    path("join-family/<uuid:token>/", views.join_family, name="join_family"),
    path("fam/<int:family_id>/", views.family_info, name="family_info"),
    # food
    path("all_food_items/", views.all_food, name="all_food"),
    path("food/<slug:slug>/", views.food_detail, name="food_detail"),
    path("add_food/", views.add_food, name="add_food"),
    path("choose_add_food/", views.choose_add_food, name="choose_add_food"),
    path(
        "food/<slug:slug>/expired/",
        views.place_in_expired_items,
        name="place_in_expired_items",
    ),
    path("api/search-food/", views.search_openfoodfacts, name="search_food_api"),
    path("food/<slug:slug>/delete", views.food_item_delete, name="food-delete"),
    path("food/<slug:slug>/edit/", views.food_edit, name="food_edit"),
    # cateegories
    path("categories/", views.category_list, name="category"),
    path("categories/delete/<int:pk>/", views.delete_category, name="delete_category"),
    # exp
    # path("expiry/manage/<int:item_id>/", views.manage_expiry, name="manage_expiry"),
    path("expiry/delete/<int:pk>/", views.delete_expiry, name="delete_expiry"),
    # Item archiving/restoring
    path("item/delete/<int:pk>/", views.delete_item, name="delete_item"),
    path("item/restore/<int:pk>/", views.restore_item, name="restore_item"),
    # Expired items page
    path("items/expired/", views.expired_items, name="expired_items"),
    # other items
    path("all_other_items/", views.all_other, name="all_other_items"),
    path("other/<slug:slug>/", views.other_detail, name="other_detail"),
    path("choose_add_other/", views.choose_add_other, name="choose_add_other"),
    path("add_other_items/", views.add_other_items, name="add_other"),
    path("other/<slug:slug>/delete/", views.other_item_delete, name="other-delete"),
    path("other/<slug:slug>/edit/", views.other_edit, name="other_edit"),
    # shopping
    path("shopping_lists/", views.all_shopping_list, name="all_shopping_list"),
    path("shopping_lists/create/", views.add_shopping_list, name="add_shopping_list"),
    path(
        "shopping_lists/<slug:slug>/",
        views.view_shopping_list,
        name="view_shopping_list",
    ),
    path(
        "shopping_lists/<slug:slug>/edit/",
        views.edit_shopping_list,
        name="edit_shopping_list",
    ),
    path(
        "shopping_lists/<slug:slug>/delete/",
        views.delete_shopping_list,
        name="delete_shopping_list",
    ),
    path(
        "shopping_lists/<slug:slug>/add_item/",
        views.add_shopping_item,
        name="add_shopping_item",
    ),
    path(
        "shopping_lists/<slug:slug>/send_email/",
        views.send_mail_shopping,
        name="send_shopping_email",
    ),
    path(
        "shop_item/<slug:slug>/edit/",
        views.edit_shopping_item,
        name="edit_shopping_item",
    ),
    path(
        "shop_item/<slug:slug>/delete/",
        views.delete_shopping_item,
        name="delete_shopping_item",
    ),
    # profile
    path("profile/", views.profile_detail, name="my_profile"),
    path("profile/<int:id>/", views.profile_detail, name="profile_detail"),
    path("profile/<int:id>/edit/", views.edit_profile, name="edit_profile"),
    # memebers
    path("family/members/", views.all_members, name="members"),
    path("family/edit/<int:member_id>/", views.edit_member_view, name="edit_member"),
    # settings
    path("settings/", views.user_settings, name="settings"),
    path("settings/change_password/", views.change_password, name="change_password"),
    path("settings/delete_account/", views.delete_account, name="delete_account"),
    path("settings/change_email/", views.change_email, name="change_email"),
    path("searchbar/", views.search_bar, name="search_bar"),
    path("search/", views.search, name="search"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
