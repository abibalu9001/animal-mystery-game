from django.core.management.base import BaseCommand

from django.core.mail import EmailMultiAlternatives

from django.conf import settings

from collections import defaultdict

from datetime import datetime

from game.models import (
    PlayerProfile,
    GameHistory,
    MonthlyReward
)


class Command(BaseCommand):

    help = "Calculate monthly rewards"


    def handle(self, *args, **kwargs):

        # =============================================
        # CURRENT MONTH
        # =============================================

        today = datetime.now()

        month = today.month 

        year = today.year

        # January case

        if month == 0:

            month = 12

            year -= 1

        # =============================================
        # FILTER MONTHLY GAMES
        # =============================================

        games = GameHistory.objects.filter(

            played_at__year=year,

            played_at__month=month

        )

        if not games.exists():

            self.stdout.write(
                self.style.WARNING(
                    "No games found for month."
                )
            )

            return

        # =============================================
        # MONTHLY CHAMPION
        # =============================================

        highest_score = max(
            g.score for g in games
        )

        champion_games = [

            g for g in games

            if g.score == highest_score

        ]

        for game in champion_games:

            MonthlyReward.objects.create(

                exists = MonthlyReward.objects.filter(

                    player=game.player,

                    reward_type="Monthly Champion",

                    month=month,

                    year=year

                ).exists()

                if not exists:

                    MonthlyReward.objects.create(

                        player=game.player,

                        reward_type="Monthly Champion",

                        month=month,

                        year=year,

                        value=f"Score: {game.score}%"

                    )

            )



        # =============================================
        # MOST ACTIVE PLAYER
        # =============================================

        activity = defaultdict(int)

        days_active = defaultdict(set)

        for game in games:

            activity[game.player] += 1

            days_active[game.player].add(
                game.played_at.date()
            )

        max_games = max(activity.values())

        active_players = [

            player

            for player, count in activity.items()

            if count == max_games

        ]

        for player in active_players:
            exists = MonthlyReward.objects.filter(

                player=game.player,

                reward_type="Monthly Champion",

                month=month,

                year=year

            ).exists()

            if not exists:

                MonthlyReward.objects.create(

                    player=player,

                    reward_type="Most Active Player",

                    month=month,

                    year=year,

                    value=f"Games Played: {max_games}"

                )



        # =============================================
        # LOWEST AI COST
        # =============================================

        lowest_cost = min(
            g.ai_cost for g in games
        )

        cheap_games = [

            g for g in games

            if g.ai_cost == lowest_cost

        ]

        for game in cheap_games:

            exists = MonthlyReward.objects.filter(

                player=game.player,

                reward_type="Lowest AI Cost",

                month=month,

                year=year

            ).exists()

            if not exists:

                MonthlyReward.objects.create(

                    player=game.player,

                    reward_type="Lowest AI Cost",

                    month=month,

                    year=year,

                    value=f"AI Cost: ₹{round(game.ai_cost,3)}"

                )



        self.stdout.write(

            self.style.SUCCESS(

                "Monthly rewards calculated successfully."

            )

        )


    # =================================================
    # EMAIL FUNCTION
    # =================================================

