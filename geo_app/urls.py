from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse, re_path

from . import views

app_name = 'geo_app'

urlpatterns = [
    # main pages
    path('', views.landing, name='landing'),
    path('admin_profile_create/', views.admin_profile_create, name='adminProfileCreate'),
    path('map/', views.MapView.as_view(), name='mapView'),
    # auth and reg
    path('signup/', views.sign_up, name='signp'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    # profile
    path('profile/', views.my_profile_show, name='profilePage'),
    path('profile/edit/general/', views.profile_edit_general, name='profileEditPage'),
    path('profile/edit/password/', views.profile_edit_password, name='profileEditPasswordPage'),
    path('profile/<str:username>/', views.profile_show, name='otherProfilePage'),
    path('profile/articles/map/<str:username>/', views.ProfileArticles.as_view(), name='profileArticlesMap'),
    path('profile/articles/list/<str:username>/', views.ProfileArticlesList.as_view(), name='profileArticlesList'),
    path('profile/stats/<str:username>/', views.ProfileStats.as_view(), name='profileArticles'),
    path('profile/trips/<str:username>', views.ProfileTrips.as_view(), name='profileTrips'),
    # articles
    path('articles/add', login_required(views.article_add), name='articleAdd'),
    path('articles/list', views.ArticlesList.as_view(), name='articles'),
    path('articles/<int:pk>', views.ArticleDetail.as_view(), name='articleDetail'),
    path('articles/edit/<int:pk>', login_required(views.ArticleEdit.as_view()), name='articleEdit'),
    path('articles/delete/<int:pk>', login_required(views.ArticleDelete.as_view()), name='articleDelete'),
    # trips
    path('trips/add', login_required(views.trip_add), name='tripAdd'),
    path('chat/<str:room_name>/', views.chatroom, name='chatroom'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

