from django.contrib import admin
from django.urls import path 
from users.views import CommentView, GroupControlView, GroupMembersView, GroupView, LikeView, NotificationView, PostView, LoginView, SignUpView , userView , LogoutView


urlpatterns = [
    path('signup', SignUpView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('user/', userView.as_view(), name="user-detail"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('posts/', PostView.as_view(), name="post-list"),
    path('posts/<int:post_id>/', PostView.as_view(), name="post-detail"),
    path('likes', LikeView.as_view(), name="like"),
    path('likes/<int:like_id>', LikeView.as_view(), name="like"),
    path('comments', CommentView.as_view(), name="comments"),
    path('comments/<int:comment_id>', CommentView.as_view(), name="comment-detail"),
    path('notification', NotificationView.as_view() , name="notification"),
    path('groups/<int:group_id>/members/', GroupMembersView.as_view(), name='group-members'),
    path('groups/<int:pk>/', GroupView.as_view(), name='group-detail'),
    path('groups/<int:group_id>/control/', GroupControlView.as_view(), name='group-control'),
]

