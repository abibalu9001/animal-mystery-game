from django.shortcuts import render, redirect

import random
import math
import os
import calendar

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

        request.session["logged_in"] = True

        request.session["email"] = email

        # check whether profile exists

        player_exists = PlayerProfile.objects.filter(
            email=email
        ).exists()

        # existing user

        if player_exists:

            return redirect("/profile/")

        # new user

        else:

            return redirect("/setup-profile/")

    return render(request, "login.html")


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

    if not player:

        return redirect("/setup-profile/")

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

    return render(request, "profile.html", {

        "player": player,

        "remaining_games": player.remaining_games,

        "total_games": player.total_games_played,

        "total_avg": player.total_average_score,

        "total_max": player.max_score,

        "stats": stats_dict

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

    player = PlayerProfile.objects.get(
        email=email
    )

    # prevent no-games exploit

    if player.remaining_games <= 0:

        return redirect("/payment/")

    # =============================================
    # START NEW GAME
    # =============================================

    if request.method == "POST" and "level" in request.POST:

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

        request.session["won"] = False

        player.remaining_games -= 1

        player.save()

    # no active game

    if "animal" not in request.session:

        return redirect("/profile/")

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

    player = PlayerProfile.objects.get(
        email=email
    )

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

    # lost games => 0

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
# MONTHLY REWARDS PAGE
# =====================================================

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


# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    request.session.flush()

    return redirect("/")
