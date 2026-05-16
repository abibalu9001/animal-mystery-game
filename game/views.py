from django.shortcuts import render, redirect

import random
import math
import os
import calendar

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from google import genai

from .models import (

    PlayerProfile,

    GameHistory,

    LevelStats,

    MonthlyReward

)

from .animal_loader import get_random_animal
from .image_url import get_wikipedia_image



# =====================================================
# GEMINI CLIENT
# =====================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =====================================================
# LEVEL FACTORS
# =====================================================

level_factor = {

    "Beginner": 0.8,

    "Easy": 0.9,

    "Medium": 1.0,

    "Hard": 1.11,

    "Expert": 1.25

}


# =====================================================
# HOME PAGE
# =====================================================


def home_view(request):

    if request.session.get("logged_in"):

        return redirect("/profile/")

    return render(request, "home.html")


# =====================================================
# LOGIN PAGE
# =====================================================


def login_view(request):

    if request.session.get("logged_in"):

        return redirect("/profile/")

    if request.method == "POST":

        email = request.POST.get("email")

        otp = random.randint(100000, 999999)

        request.session["otp"] = str(otp)

        request.session["pending_email"] = email

        subject = "Animal Mystery OTP Verification"

        from_email = settings.EMAIL_HOST_USER

        to = [email]

        text_content = f"Your OTP is {otp}"

        html_content = f"""
        <div style='font-family:Arial;background:#0f172a;color:white;padding:40px;border-radius:20px;'>

        <h1 style='color:#facc15;text-align:center;'>🐾 Animal Mystery</h1>

        <p style='font-size:20px;'>
        Welcome to Animal Mystery.
        </p>

        <p style='font-size:20px;'>
        Use the OTP below to continue login.
        </p>

        <div style='background:#1e293b;padding:30px;border-radius:18px;text-align:center;margin-top:35px;'>

        <span style='font-size:50px;font-weight:bold;color:#facc15;letter-spacing:12px;'>

        {otp}

        </span>

        </div>

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

        return redirect("/verify-otp/")

    return render(request, "login.html")


# =====================================================
# VERIFY OTP
# =====================================================


def verify_otp_view(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        real_otp = request.session.get("otp")

        email = request.session.get("pending_email")

        if entered_otp == real_otp:

            request.session["logged_in"] = True

            request.session["email"] = email

            player_exists = PlayerProfile.objects.filter(
                email=email
            ).exists()

            if player_exists:

                return redirect("/profile/")

            else:

                return redirect("/setup-profile/")

    return render(request, "verify_otp.html")


# =====================================================
# PROFILE SETUP
# =====================================================


def setup_profile_view(request):

    if request.method == "POST":

        username = request.POST.get("username")

        state = request.POST.get("state")

        district = request.POST.get("district")

        email = request.session.get("email")

        if PlayerProfile.objects.filter(
            email=email
        ).exists():

            return redirect("/profile/")

        PlayerProfile.objects.create(

            email=email,
            username=username,
            state=state,
            district=district,
            total_average_score=0,
            max_score=0,
            total_games_played=0,
            total_ai_cost=0,
            remaining_games=100

        )

        return redirect("/profile/")

    return render(request, "setup_profile.html")


# =====================================================
# PROFILE PAGE
# =====================================================


def profile_view(request):

    if not request.session.get("logged_in"):

        return redirect("/login/")

    email = request.session.get("email")

    player = PlayerProfile.objects.filter(
        email=email
    ).first()

    all_stats = LevelStats.objects.filter(
        player=player
    )

    stats_dict = {}

    for s in all_stats:

        stats_dict[s.level] = {

            "games": s.games_played,

            "avg": s.average_score,

            "max": s.max_score

        }

    if not player:

        return redirect("/setup-profile/")

    return render(request, "profile.html", {

        "player": player,

        "remaining_games": player.remaining_games,

        "total_games": player.total_games_played,

        "total_avg": player.total_average_score,

        "total_max": player.max_score,

        "stats": stats_dict,

    })


# =====================================================
# INSTRUCTIONS PAGE
# =====================================================


def instructions_view(request):

    if not request.session.get("logged_in"):

        return redirect("/login/")

    return render(request, "instructions.html")


# =====================================================
# GAME PAGE
# =====================================================


def game_view(request):

    if not request.session.get("logged_in"):

        return redirect("/login/")

    email = request.session.get("email")

    player = PlayerProfile.objects.get(email=email)

    if "animal" not in request.session:

        level = request.POST.get(
            "level",
            "Medium"
        )

        selected = get_random_animal(level)

        request.session["animal"] = selected["animal"]

        request.session["level"] = selected["level"]

        request.session["questions"] = 0

        request.session["wrong"] = 0

        request.session["cost"] = 0

        player.remaining_games -= 1

        player.save()

    animal = request.session["animal"]

    questions = request.session["questions"]

    wrong = request.session["wrong"]

    cost = request.session["cost"]

    level = request.session["level"]

    answer = ""

    if request.method == "POST":

        action = request.POST.get("action")

        # =========================================
        # ASK QUESTION
        # =========================================

        if action == "ask":

            question = request.POST.get("question")

            if len(question.split()) > 15:

                answer = "Question too long"

            else:

                response = client.models.generate_content(

                    model="gemini-2.5-flash",

                    contents=f"""
Animal: {animal}

Reply ONLY with:
1
0
or
2

1 = yes
0 = no
2 = invalid/non-boolean question

Question:
{question}
"""
                )

                ai_answer = response.text.strip()

                if ai_answer == "1":

                    answer = "Yes"

                    questions += 1

                elif ai_answer == "0":

                    answer = "No"

                    questions += 1

                else:

                    answer = "Invalid Question"

                usage = response.usage_metadata

                input_cost = (
                    usage.prompt_token_count / 1_000_000
                ) * 0.3

                output_cost = (
                    usage.candidates_token_count / 1_000_000
                ) * 2.5

                cost += (
                    input_cost + output_cost
                ) * 95.65

        # =========================================
        # GUESS ANIMAL
        # =========================================

        elif action == "guess":

            guess = request.POST.get("guess")

            if guess.lower().strip() == animal.lower():

                request.session["won"] = True

                return redirect("/result/")

            else:

                wrong += 1

                answer = "Wrong Guess"

        request.session["questions"] = questions

        request.session["wrong"] = wrong

        request.session["cost"] = cost

        # lose condition

        if questions >= 20:

            request.session["won"] = False

            return redirect("/result/")

    return render(request, "game.html", {

        "questions_left": 20 - questions,

        "cost": round(cost, 3),

        "wrong": wrong,

        "answer": answer

    })


# =====================================================
# RESULT PAGE
# =====================================================


def result_view(request):

    if not request.session.get("logged_in"):

        return redirect("/login/")

    email = request.session.get("email")

    player = PlayerProfile.objects.get(email=email)

    questions = request.session.get("questions", 0)

    wrong = request.session.get("wrong", 0)

    cost = request.session.get("cost", 0)

    animal = request.session.get(
        "animal",
        "Unknown"
    ).title()

    level = request.session.get(
        "level",
        "Medium"
    )

    won = request.session.get("won")

    try:

        image_url = get_wikipedia_image(animal)

    except:

        image_url = None

    L = level_factor[level]

    score = (

        100

        * (1 - (questions / (25 * L)))

        * math.exp(-(10 * cost + 0.3 * wrong))

    )

    score = round(score, 2)

    if not won:

        score = 0

    # =============================================
    # SAVE GAME HISTORY
    # =============================================

    GameHistory.objects.create(

        player=player,

        username=player.username,

        state=player.state,

        district=player.district,

        level=level,

        animal=animal,

        score=score,

        won=won,

        ai_cost=cost,

        questions_used=questions,

        wrong_tries=wrong

    )
    # =============================================
    # UPDATE LEVEL STATS
    # =============================================

    stats, created = LevelStats.objects.get_or_create(

        player=player,

        level=level

    )

    stats.games_played += 1

    stats.total_score += score

    stats.average_score = round(

        stats.total_score
        /
        stats.games_played,

        2

    )

    if score > stats.max_score:

        stats.max_score = score

    stats.save()

    # =============================================
    # UPDATE PLAYER PROFILE
    # =============================================

    player.total_games_played += 1

    player.total_ai_cost += cost

    if score > player.max_score:

        player.max_score = score

    player.total_average_score = round(

        (
            player.total_average_score
            * (player.total_games_played - 1)
            + score
        )
        /
        player.total_games_played,

        2

    )

    player.save()

    # clear sessions

    request.session.pop("animal", None)
    request.session.pop("questions", None)
    request.session.pop("wrong", None)
    request.session.pop("cost", None)
    request.session.pop("level", None)
    request.session.pop("won", None)

    return render(request, "result.html", {

        "animal": animal,

        "score": score,

        "questions_used": questions,

        "wrong_guesses": wrong,

        "cost": round(cost, 3),

        "won": won,

        "image_url": image_url,

        "level": level

    })


# =====================================================
# PAYMENT PAGE
# =====================================================


def payment_view(request):

    if not request.session.get("logged_in"):

        return redirect("/login/")

    return render(request, "payment.html")


# =====================================================
# PAYMENT SUCCESS
# =====================================================


def payment_success_view(request):

    email = request.session.get("email")

    player = PlayerProfile.objects.get(
        email=email
    )

    player.remaining_games += 100

    player.save()

    return redirect("/profile/")


# =====================================================
# LOGOUT
# =====================================================


def logout_view(request):

    request.session.flush()

    return redirect("/")

def monthly_rewards_view(request):

    if not request.session.get("logged_in"):

        return redirect("/login/")

    email = request.session.get("email")

    player = PlayerProfile.objects.get(
        email=email
    )

    rewards = MonthlyReward.objects.filter(
        player=player
    ).order_by("-year", "-month")

    formatted_rewards = []

    for reward in rewards:

        month_name = calendar.month_name[
            reward.month
        ]

        formatted_rewards.append({

            "reward_type": reward.reward_type,

            "month": f"{month_name} {reward.year}",

            "value": reward.value

        })

    return render(

        request,

        "monthly_rewards.html",

        {

            "rewards": formatted_rewards

        }

    )
