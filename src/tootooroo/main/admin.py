from django.contrib import admin
from main.models import CustomUser, Toot, Follow, Reply, Like, Retoot, Hashtag

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'created_at', 'updated_at')
    search_fields = ('user__username', 'bio')

class TootAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'updated_at', 'original_toot')
    search_fields = ('user__user__username', 'content')
    list_filter = ('created_at', 'updated_at')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__user__username', 'following__user__username')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('toot', 'user', 'content', 'created_at', 'updated_at')
    search_fields = ('toot__content', 'user__user__username', 'content')
    list_filter = ('created_at', 'updated_at')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('toot', 'user', 'created_at')
    search_fields = ('toot__content', 'user__user__username')
    list_filter = ('created_at',)

class RetootAdmin(admin.ModelAdmin):
    list_display = ('toot', 'user', 'created_at')
    search_fields = ('toot__content', 'user__user__username')
    list_filter = ('created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Toot, TootAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Retoot, RetootAdmin)
admin.site.register(Hashtag)