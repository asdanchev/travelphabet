from django.urls import path, re_path, include
from . import views
from django.contrib.auth.views import LogoutView, LoginView

urlpatterns = [
    # Home page
    path('', views.index, name='home'),

    path('login/', LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # CKEditor file upload
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Admin dashboard
    path('asdanchev/dashboard/', views.dashboard, name='dashboard'),
    path('asdanchev/create/', views.create_article, name='create_article'),
    path('asdanchev/edit/<int:pk>/', views.edit_article, name='edit_article'),
    path('asdanchev/delete/<int:pk>/', views.delete_article, name='delete_article'),

    # Articles by category (e.g. /place/dubai/)
    path('place/<slug:category>/', views.articles_by_category, name='articles_by_category'),

    # Article detail page (supports Cyrillic and Latin slugs)
    re_path(r'^(?P<letter>[a-zA-Z]+)/(?P<slug>[-\w]+)/$', views.article_detail, name='article_detail'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # All articles page
    path('articles/', views.article_list, name='article_list'),
    
    # Letter archive page (e.g. /a/)
    path('<str:letter>/', views.letter_view, name='letter'),
]