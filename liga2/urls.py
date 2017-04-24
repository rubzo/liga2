from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),

    url(r"^tournament/(?P<tournament_id>[0-9]+)/$", views.tournament_view, name="tournament_view"),

    url(r"^tournament/new/$", views.tournament_add, name="tournament_add"),
    url(r"^player/new/$", views.player_add, name="player_add"),

    url(r"^player/(?P<player_id>[0-9]+)/edit$", views.player_edit, name="player_edit"),
    url(r"^match/(?P<match_id>[0-9]+)/edit$", views.match_edit, name="match_edit"),

    url(r"^player/(?P<pk>[0-9]+)/delete$", views.PlayerDelete.as_view(), name="player_delete"),
    url(r"^tournament/(?P<pk>[0-9]+)/delete$", views.TournamentDelete.as_view(), name="tournament_delete"),
]
