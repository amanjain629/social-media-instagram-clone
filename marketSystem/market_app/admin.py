from re import T
from django.contrib import admin
from market_app.models import Post,Follow,Tag,Stream
# Register your models here.

admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Stream)