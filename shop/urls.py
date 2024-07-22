from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
     path("admin/", admin.site.urls, name="Admin"),
    path("accounts/", include("allauth.urls")),
    path("profile/", views.profile,name="Profile"),
    path("Home", views.home, name="Home"),
    path("", views.home, name="Home"),
    path("About", views.about, name="About"),
    path("PagesFaq", views.pages_faq, name="PagesFaq"),
    path("File", views.file_list, name="file_list"),
    path("folder/<int:folder_id>/", views.file_list, name="file_list"),
    path("upload/", views.upload_file, name="upload_file"),
    path("upload/<int:folder_id>/", views.upload_file, name="upload_file"),
    path("folder/create/", views.create_folder, name="create_folder"),
    path("folder/create/<int:parent_id>/",
         views.create_folder, name="create_folder"),
    path("download/<int:file_id>/", views.download_file, name="download_file"),
    path("delete/file/<int:file_id>/", views.delete_file, name="delete_file"),
    path("delete/folder/<int:folder_id>/",
         views.delete_folder, name="delete_folder"),
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("post/new/", views.add_blog_post, name="add_blog_post"),
    path("ajax/like/<int:pk>/", views.ajax_like_post, name="ajax_like_post"),
    path("review/", views.review_posts, name="review_posts"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),
    path("post/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("comment/<int:pk>/edit/", views.edit_comment, name="edit_comment"),

    path("upload/", views.blog_file, name="blog_file"),
    path("Ocr/", views.ocr, name="Ocr"),
    path("tetris-game/", views.tetris_game, name="tetris_game"),
    
    path("Me", views.me, name="me"),
    
    path('fetch-news/', views.fetch_news, name='fetch_news'),
]
