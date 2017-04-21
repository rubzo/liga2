from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^tournaments/(?P<tournament_id>[0-9]+)/$", views.tournament_view, name="tournament_view"),
    #url(r"^tournaments/add/$", views.tournament_add, name="tournament_add"),

    #url(r"^api/players/$", views.api_players_list, name="api_players_list"),
    #url(r"^api/players/add$", views.api_players_add, name="api_players_add"),
    #url(r"^api/tournaments/$", views.api_tournaments_list, name="api_tournaments_list"),
]
