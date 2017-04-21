from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

from .models import Tournament, Match, Player, Participation

def index(request):
    tournaments = Tournament.objects.all()
    context = {"tournaments": tournaments}
    return render(request, "liga2/index.html", context)

def _calculate_player_info(tournament, player):
    player_info = {}

    player_matches = Match.objects.filter(players=player).filter(complete=True)
    win_count = 0
    seconds_count = 0
    draw_count = 0
    loss_count = 0
    for match in player_matches:
        participants = Participation.objects.filter(match=match)

        scores = []
        for p in participants:
            scores.append((p.score, p.player))
        scores = sorted(scores)[::-1]

        if scores[0][1] == player:
            if scores[0][0] == scores[1][0]:
                draw_count += 1
            else:
                win_count += 1
        elif tournament.second_place_points != 0 and scores[1][1] == player:
            seconds_count += 1
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
        player_list.append((player_info["points"], player_info))

    player_list = sorted(player_list)[::-1]

    context = {"tournament": tournament,
            "players": [p for (_,p) in player_list]}

    return render(request, "liga2/tournament_view.html", context)

def tournament_add(request):
    return HttpResponse("Oh you want to add a tournament?")
