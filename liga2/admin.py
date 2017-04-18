from django.contrib import admin

from .models import Player, Match, Tournament, Participation

admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Tournament)
admin.site.register(Participation)
