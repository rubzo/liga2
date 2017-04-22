from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

from .models import Tournament, Match, Player, Participation

def index(request):
    tournaments = Tournament.objects.all()
    context = {"tournaments": tournaments}
    return render(request, "liga2/index.html", context)

def _generate_matches(tournament):
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
    return render(request, "liga2/tournament_add.html")
