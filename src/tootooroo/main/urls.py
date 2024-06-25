from django.urls import path
from main import views

urlpatterns = [
    path('', views.top, name='top'),  # トップページ
#    path('toot/new/', views.toot_new, name='toot_new'),  # トゥート新規作成ページ
#    path('toot/<int:pk>/', views.toot_detail, name='toot_detail'),  # トゥート詳細ページ
#    path('toot/<int:pk>/edit/', views.toot_edit, name='toot_edit'),  # トゥート編集ページ
#    path('toot/<int:pk>/delete/', views.toot_delete, name='toot_delete'),  # トゥート削除ページ
#    path('users/<int:pk>/', views.user_detail, name='user_detail'),  # ユーザー詳細ページ
#    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),  # ユーザー情報編集ページ
#    path('users/<int:pk>/follow/', views.user_follow, name='user_follow'),  # ユーザーのフォロー・アンフォローページ
#    path('users/<int:pk>/followers/', views.user_followers, name='user_followers'),  # ユーザーのフォロワー一覧ページ
#    path('users/<int:pk>/following/', views.user_following, name='user_following'),  # ユーザーがフォローしているユーザー一覧ページ
#    path('users/<int:pk>/toots/', views.user_toots, name='user_toots'),  # ユーザーのトゥート一覧ページ
]

