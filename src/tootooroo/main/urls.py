from django.urls import path,re_path
from main import views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from .views import HashtagDetailView

urlpatterns = [
    path('', views.root_view, name='root'),
    path('top/', views.TopView.as_view(), name='top'),
    path('toot/new/', views.TootCreateView.as_view(), name='toot_new'),
    path('toot/<int:pk>/', views.TootDetailView.as_view(), name='toot_detail'),
    path('toot/<int:pk>/edit/', views.TootUpdateView.as_view(), name='toot_edit'),
    path('toot/<int:pk>/delete/', views.delete_toot, name='delete_toot'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    # path('user/<int:pk>/follow/', views.UserFollowView.as_view(), name='user_follow'),
    path('user/<int:pk>/followers/', views.UserFollowersView.as_view(), name='user_followers'),
    path('user/<int:pk>/following/', views.UserFollowingView.as_view(), name='user_following'),
    # path('user/<int:pk>/unfollow/', views.user_unfollow, name='user_unfollow'),
    # path('user/<int:pk>/follow/', views.user_follow, name='user_follow'),
    path('user/<int:pk>/follow/', views.follow_user, name='user_follow'),
    path('user/<int:pk>/unfollow/', views.unfollow_user, name='user_unfollow'),
    path('user/<int:pk>/toots/', views.UserTootsView.as_view(), name='user_toots'),
    path('toot/<int:pk>/reply/', views.ReplyCreateView.as_view(), name='reply_new'),
    path('toot/<int:pk>/like/', views.LikeTootView.as_view(), name='like_toot'),
    path('toot/<int:pk>/retoot/', views.RetootCreateView.as_view(), name='retoot'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True, template_name='toot/login.html',next_page='top'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', CreateView.as_view(template_name='toot/signup.html', form_class=UserCreationForm, success_url='/',), name='signup'),
    path('user/<int:user_id>/liked_toots/', views.UserLikedTootsView.as_view(), name='user_liked_toots'),
    path('toot/<int:pk>/likess/', views.TootLikesView.as_view(), name='toot_likess'),
    path('search/', views.search, name='search'), 
    path('reply/<int:pk>/delete/', views.delete_reply, name='delete_reply'),
    path('toot/<int:pk>/reply/', views.ReplyCreateView.as_view(), name='reply_new'),
    path('hashtag/<int:id>/', views.HashtagDetailView.as_view(), name='hashtag_detail'),
    path('toot/<int:toot_id>/likes/', views.toot_likes, name='toot_likes'),
    path('change-background-color/', views.change_background_color, name='change_background_color'),

]
