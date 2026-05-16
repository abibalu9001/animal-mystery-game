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

            # send email

            self.send_reward_email(

                player=game.player,

                reward_name="🥇 Monthly Champion",

                month=month,

                year=year,

                details=f"""

Animal: {game.animal}

Difficulty: {game.level}

Final Score: {game.score}%

Questions Used: {game.questions_used}

"""
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

            self.send_reward_email(

                player=player,

                reward_name="🔥 Most Active Player",

                month=month,

                year=year,

                details=f"""

Total Games Played: {max_games}

Active Days: {len(days_active[player])}

"""
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

            self.send_reward_email(

                player=game.player,

                reward_name="💎 Lowest AI Cost",

                month=month,

                year=year,

                details=f"""

Animal: {game.animal}

Difficulty: {game.level}

AI Cost: ₹{round(game.ai_cost,3)}

Questions Used: {game.questions_used}

"""
            )

        self.stdout.write(

            self.style.SUCCESS(

                "Monthly rewards calculated successfully."

            )

        )


    # =================================================
    # EMAIL FUNCTION
    # =================================================

    def send_reward_email(

        self,

        player,

        reward_name,

        month,

        year,

        details

    ):

        month_name = datetime(

            year,

            month,

            1

        ).strftime("%B %Y")

        subject = f"{reward_name} - {month_name}"

        from_email = settings.EMAIL_HOST_USER

        to = [player.email]

        text_content = (

            f"Congratulations!\n\n"

            f"You earned:\n"

            f"{reward_name}\n\n"

            f"{details}"

        )

        html_content = f"""

<div style="
    font-family: Arial;
    background: #0f172a;
    color: white;
    padding: 40px;
    border-radius: 20px;
">

    <h1 style="
        color: #facc15;
        text-align: center;
        font-size: 42px;
    ">

        {reward_name}

    </h1>

    <p style="
        font-size: 22px;
        margin-top: 30px;
        line-height: 1.8;
    ">

        Congratulations
        <b>{player.username}</b>!

    </p>

    <p style="
        font-size: 20px;
        line-height: 1.8;
    ">

        You earned this achievement for:

        <b>{month_name}</b>

    </p>

    <div style="
        background: #1e293b;
        padding: 30px;
        border-radius: 18px;
        margin-top: 30px;
        line-height: 2;
        font-size: 20px;
    ">

        {details.replace(chr(10), '<br>')}

    </div>

    <p style="
        color: #cbd5e1;
        font-size: 18px;
        margin-top: 35px;
    ">

        Keep playing Animal Mystery
        and continue your winning streak.

    </p>

    <p style="
        text-align: center;
        margin-top: 30px;
        color: #64748b;
    ">

        🐾 Animal Mystery Team

    </p>

</div>

"""

        email_message = EmailMultiAlternatives(

            subject,

            text_content,

            from_email,

            to

        )

        email_message.attach_alternative(

            html_content,

            "text/html"

        )

        email_message.send()
