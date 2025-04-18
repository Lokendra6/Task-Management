# users/urls.py

from django.urls import path

from .views import UserListCreateAPIView, UserDetailAPIView,ManageUserAPIView

urlpatterns = [
    
   
   
    
    path('users/', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<int:user_id>/manage/',ManageUserAPIView.as_view(),name='manage-user'),
]
