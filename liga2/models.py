from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField(max_length=512)
    players_per_match = models.IntegerField(default=2)
    individual_matches = models.IntegerField(default=4)

    win_points = models.IntegerField(default=3)
    draw_points = models.IntegerField(default=2)
    second_place_points = models.IntegerField(default=0)
    loss_points = models.IntegerField(default=0)

    players = models.ManyToManyField(Player)

    def __str__(self):
        return self.name


class Match(models.Model):
    players = models.ManyToManyField(Player, through="Participation")
    complete = models.BooleanField(default=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        done = "(TBD)"
        if self.complete:
            done = "(DONE)"
        return "{} {}".format(" vs. ".join([p.name for p in self.players.all()]), done)


class Participation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return "{} in {} ({})".format(self.player.name, self.match, self.score)
