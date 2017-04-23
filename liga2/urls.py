from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^tournament/(?P<tournament_id>[0-9]+)/$", views.tournament_view, name="tournament_view"),
    url(r"^tournament/add/$", views.tournament_add, name="tournament_add"),
    url(r"^player/add/$", views.player_add, name="player_add"),
    url(r"^player/(?P<player_id>[0-9]+)/edit$", views.player_edit, name="player_edit"),
]
