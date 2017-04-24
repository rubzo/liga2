from django import forms

from .models import Tournament, Player

class TournamentForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = (
                "name",
                "players_per_match",
                "individual_matches",
                "win_points",
                "draw_points",
                "second_place_points",
                "loss_points",
                "players"
                )

        widgets = {
                "name": forms.TextInput(attrs={"autofocus": ""}),
                "players": forms.CheckboxSelectMultiple(attrs={"checked": ""})
                }

class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = (
                "name",
                )

        widgets = {
                "name": forms.TextInput(attrs={"autofocus": "autofocus"})
                }
