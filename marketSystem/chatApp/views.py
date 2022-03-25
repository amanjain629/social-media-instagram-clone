from django.shortcuts import render

# Create your views here.
def allChatsView(request):
    return render(request,'allChat.html')

def RoomView(request,room):
    return render(request,'room.html')

def checkRoomView(request):
    pass