import pyrebase

from django.shortcuts import render, redirect, get_object_or_404
from authy.forms import EditProfileForm, SignupForm, ChangePasswordForm, veriffyidForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from authy.models import Profile
# from post.models import Post, Follow, Stream
from django.db import transaction
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.core.paginator import Paginator

from django.urls import resolve

from market_app.models import Follow, Post, Stream


config = {
  "apiKey": "AIzaSyCLGGkmb84Kv2ulymsVvMJ9Ex8rwovVlW4",
  "authDomain": "chatapp-7a2a1.firebaseapp.com",
  "databaseURL": "https://chatapp-7a2a1-default-rtdb.firebaseio.com",
  "projectId": "chatapp-7a2a1",
  "storageBucket": "chatapp-7a2a1.appspot.com",
  "messagingSenderId": "749633545022",
  "appId": "1:749633545022:web:6b6b1e7b2c0b901ab8826f",
  "measurementId": "G-SXF491ZZV0"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
storage = firebase.storage()


# Create your views here.
def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)
	url_name = resolve(request.path).url_name
	
	if url_name == 'profile':
		posts = Post.objects.filter(user=user).order_by('-posted')

	else:
		posts = profile.favorites.all()

	#Profile info box
	posts_count = Post.objects.filter(user=user).count()
	following_count = Follow.objects.filter(follower=user).count()
	followers_count = Follow.objects.filter(following=user).count()

	#follow status
	follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

	#Pagination
	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page')
	posts_paginator = paginator.get_page(page_number)

	template = loader.get_template('profile.html')

	context = {
		'posts': posts_paginator,
		'profile':profile,
		'following_count':following_count,
		'followers_count':followers_count,
		'posts_count':posts_count,
		'follow_status':follow_status,
		'url_name':url_name,
	}

	return HttpResponse(template.render(context, request))

# def UserProfileFavorites(request, username):
# 	user = get_object_or_404(User, username=username)
# 	profile = Profile.objects.get(user=user)
	
# 	posts = profile.favorites.all()

# 	#Profile info box
# 	posts_count = Post.objects.filter(user=user).count()
# 	following_count = Follow.objects.filter(follower=user).count()
# 	followers_count = Follow.objects.filter(following=user).count()

# 	#Pagination
# 	paginator = Paginator(posts, 8)
# 	page_number = request.GET.get('page')
# 	posts_paginator = paginator.get_page(page_number)

# 	template = loader.get_template('profile_favorite.html')

# 	context = {
# 		'posts': posts_paginator,
# 		'profile':profile,
# 		'following_count':following_count,
# 		'followers_count':followers_count,
# 		'posts_count':posts_count,
# 	}

# 	return HttpResponse(template.render(context, request))


def Signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, password=password)
			return redirect('edit-profile')
	else:
		form = SignupForm()
	
	context = {
		'form':form,
	}

	return render(request, 'signup.html', context)


@login_required
def PasswordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change_password_done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form':form,
	}

	return render(request, 'change_password.html', context)

def PasswordChangeDone(request):
	return render(request, 'change_password_done.html')


def verifyid(request):
	if request.user.is_authenticated:
		return redirect('index')
	if request.method == 'POST':
		form = veriffyidForm(request.POST)
		if form.is_valid():
			userid = form.cleaned_data.get('userid')
			#x = database.child('users').child(userid).get().val()
			username=(database.child('users').child(userid).child('username').get().val())
			email=(database.child('users').child(userid).child('emailid').get().val())
			password=(database.child('users').child(userid).child('password').get().val())
			user = User.objects.create(username=username, email=email)
			user.set_password(password)
			user.save()
			name = (database.child('users').child(userid).child('name').get().val())
			uid = (database.child('users').child(userid).child('uid').get().val())
			phone = (database.child('users').child(userid).child('phoneNumber').get().val())
			image = (database.child('users').child(userid).child('profileImage').get().val())  
			#EditProfile(request,userid,username)
			Profile.objects.create(user_id=user.id,name=name,email_id=email,uuid=uid,image=image,phone=phone)
			return redirect('login')
	else:
		form = veriffyidForm()

	context = {
		'form':form,
	}

	return render(request, 'verifyid.html', context)

@login_required
def EditProfile(request):
	user = request.user.id
	profile = Profile.objects.get(user__id=user)
	BASE_WIDTH = 400

	if request.method == 'POST':
		form = EditProfileForm(request.POST, request.FILES)
		if form.is_valid():
			profile.picture = form.cleaned_data.get('picture')
			profile.first_name = form.cleaned_data.get('first_name')
			profile.last_name = form.cleaned_data.get('last_name')
			profile.location = form.cleaned_data.get('location')
			profile.url = form.cleaned_data.get('url')
			profile.profile_info = form.cleaned_data.get('profile_info')
			profile.save()
			return redirect('index')
	else:
		form = EditProfileForm()

	context = {
		'form':form,
	}

	return render(request, 'edit_profile.html', context)


@login_required
def follow(request, username, option):
	following = get_object_or_404(User, username=username)

	try:
		f, created = Follow.objects.get_or_create(follower=request.user, following=following)

		if int(option) == 0:
			f.delete()
			Stream.objects.filter(following=following, user=request.user).all().delete()
		else:
			posts = Post.objects.all().filter(user=following)[:25]

			with transaction.atomic():
				for post in posts:
					stream = Stream(post=post, user=request.user, date=post.posted, following=following)
					stream.save()

		return HttpResponseRedirect(reverse('profile', args=[username]))
	except User.DoesNotExist:
		return HttpResponseRedirect(reverse('profile', args=[username]))