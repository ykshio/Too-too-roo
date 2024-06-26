from django.urls import path
from main import views

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('toot/new/', views.TootCreateView.as_view(), name='toot_new'),
    path('toot/<int:pk>/', views.TootDetailView.as_view(), name='toot_detail'),
    path('toot/<int:pk>/edit/', views.TootUpdateView.as_view(), name='toot_edit'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('user/<int:pk>/follow/', views.UserFollowView.as_view(), name='user_follow'),
    path('user/<int:pk>/followers/', views.UserFollowersView.as_view(), name='user_followers'),
    path('user/<int:pk>/following/', views.UserFollowingView.as_view(), name='user_following'),
    path('user/<int:pk>/toots/', views.UserTootsView.as_view(), name='user_toots'),
    path('toot/<int:pk>/reply/', views.ReplyCreateView.as_view(), name='reply_new'),
    path('toot/<int:pk>/like/', views.LikeTootView.as_view(), name='like_toot'),
    path('toot/<int:pk>/retoot/', views.RetootCreateView.as_view(), name='retoot'),
]


