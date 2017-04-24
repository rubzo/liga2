from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import DeleteView
from django.http import HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils import timezone

from collections import defaultdict

from .models import Tournament, Match, Player, Participation
from .forms import TournamentForm, PlayerForm

import random

def index(request):
    tournaments = Tournament.objects.all()
    players = Player.objects.all()
    context = {
            "tournaments": tournaments,
            "players": players,
            }
    return render(request, "liga2/index.html", context)


def _generate_matchups(tournament):
    """
    At this point, the tournament is setup correctly.
    Generate all the matches for the tournament.
    """
    players = tournament.players.all()

    assert len(players) > tournament.players_per_match

    matches = []

    # Algorithm adapted from:
    # http://stackoverflow.com/questions/24332311/what-algorithm-can-generate-round-robin-pairings-for-rounds-with-more-than-two

    # m denotes a legal matching of players (by index)
    m = list(range(0, tournament.players_per_match))
    # e denotes the last index in the match array
    e = len(m)-1
    # i denotes the index into the match array we're currently trying to
    # increment
    i = e
    # p denotes the last player id
    p = len(players)-1

    while i != -1:
        # assume if we're here this is a legal matching
        for _ in range(tournament.individual_matches):
            matches.append(list(m))

        # Is it time to move i?
        if (i == e and m[i] == p) or (i != e and m[i] == m[i+1]-1):
            # Move to the next slot
            i -= 1
            if i == -1:
                break
            m[i] += 1
            # Set the following slots to their lowest possible value
            j = i+1
            while j <= e:
                m[j] = m[i] + (j - i)
                j += 1
            # Start from the end, and scan until you find an increment-
            # able index
            i = e
            if m[i] != p:
                continue
            while m[i] == m[i-1]+1:
                i -= 1
                if i == -1:
                    break
        # It is not time to move i, just increment the value
        else:
            m[i] += 1

    matchups_with_players = []
    for match in matches:
        matchups_with_players.append([ players[i] for i in match ])

    return matchups_with_players


def _calculate_player_info(tournament, player):
    player_info = {}

    player_matches = Match.objects.filter(players=player, tournament=tournament).filter(complete=True)
    win_count = 0
    seconds_count = 0
    draw_count = 0
    loss_count = 0
    for match in player_matches:
        participants = Participation.objects.filter(match=match)

        scores = defaultdict(list)

        for p in participants:
            scores[p.score].append(p.player)

        u = sorted(scores.keys())[::-1]

        if player in scores[u[0]] and len(scores[u[0]]) == 1:
            win_count += 1
        elif player in scores[u[0]]:
            draw_count += 1
        elif tournament.second_place_points != 0 and player in scores[u[1]] and len(scores[u[1]]) == 1:
            secounds_count += 1
        else:
            loss_count += 1

    points = (win_count * tournament.win_points +
            draw_count * tournament.draw_points +
            seconds_count * tournament.second_place_points +
            loss_count * tournament.loss_points)

    player_info["matches"] = player_matches.count()
    player_info["wins"] = win_count
    player_info["draws"] = draw_count
    player_info["losses"] = loss_count
    player_info["points"] = points
    player_info["player"] = player

    return player_info


def tournament_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    player_list = []

    for player in tournament.players.all():
        player_info = _calculate_player_info(tournament, player)
        player_list.append(player_info)

    upcoming_match_list = list(Match.objects.filter(tournament=tournament, complete=False))
    random.shuffle(upcoming_match_list)
    completed_match_list = Match.objects.filter(tournament=tournament, complete=True).order_by("-date_complete")

    context = {
            "tournament": tournament,
            "players": player_list,
            "upcoming_matches": upcoming_match_list,
            "completed_matches": completed_match_list,
            }

    return render(request, "liga2/tournament_view.html", context)


def tournament_add(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()

            matchups = _generate_matchups(tournament)
            for matchup in matchups:
                match = Match(tournament=tournament)
                match.save()
                for player in matchup:
                    participation = Participation(player=player, match=match)
                    participation.save()

            return redirect("index")
    else:
        form = TournamentForm()
        return render(request, "liga2/tournament_edit.html", {"form": form})


def player_add(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            return redirect("index")
    else:
        form = PlayerForm()
        return render(request, "liga2/player_edit.html", {"form": form})


def player_edit(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            player = form.save()
            return redirect("index")
    else:
        form = PlayerForm(instance=player)
        return render(request, "liga2/player_edit.html", {"form": form})

def match_edit(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    if request.method == "POST":
        for (k, v) in request.POST.items():
            if k.startswith("score_"):
                participation_id = int(k.replace("score_", ""))
                participation = Participation.objects.get(id=participation_id)
                participation.score = int(v)
                participation.save()
        match.complete = True
        match.date_complete = timezone.now()
        match.save()
        return redirect("tournament_view", tournament_id=match.tournament.id)
    else:
        participations = Participation.objects.filter(match=match)
        return render(request, "liga2/match_edit.html", {"participations": participations})


class PlayerDelete(DeleteView):
    model = Player
    success_url = reverse_lazy("index")
    template_name = "liga2/object_delete.html"

    def delete(self, request, *args, **kwargs):
        try:
            return super(PlayerDelete, self).delete(request, *args, **kwargs)
        except models.ProtectedError as e:
            # Return the appropriate response
            return HttpResponseForbidden("This player is tied to 1 or more games, so cannot be deleted.")

class TournamentDelete(DeleteView):
    model = Tournament
    success_url = reverse_lazy("index")
    template_name = "liga2/object_delete.html"
