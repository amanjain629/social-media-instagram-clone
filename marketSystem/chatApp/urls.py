from . import views
from django.urls import path

urlpatterns = [
    path('allchats/',views.allChatsView,name='allchats'),
    path('<str:room>/',views.RoomView,name='room'),
    path('checkroom',views.checkRoomView,name='checkroom')
]