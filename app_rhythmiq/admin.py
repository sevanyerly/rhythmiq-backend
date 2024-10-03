from django.contrib import admin

# Register your models here.
from app_rhythmiq.models.user_profile import UserProfile
from app_rhythmiq.models.playlist import  Playlist
from app_rhythmiq.models.song import Song
from app_rhythmiq.models.genre import Genre
from app_rhythmiq.models.downloaded_song import DownloadedSong
from app_rhythmiq.models.like import Like

admin.site.register(UserProfile)
admin.site.register(Playlist)
admin.site.register(Song)
admin.site.register(Genre)
admin.site.register(DownloadedSong)
admin.site.register(Like)
