
from django.db import models


# =====================================================
# PLAYER PROFILE TABLE
# =====================================================

class PlayerProfile(models.Model):

    email = models.EmailField(
        unique=True
    )

    username = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    district = models.CharField(
        max_length=100
    )

    total_average_score = models.FloatField(
        default=0
    )

    max_score = models.FloatField(
        default=0
    )

    total_games_played = models.IntegerField(
        default=0
    )

    total_ai_cost = models.FloatField(
        default=0
    )

    remaining_games = models.IntegerField(
        default=100
    )

    def __str__(self):

        return self.username


# =====================================================
# GAME HISTORY TABLE
# =====================================================

class GameHistory(models.Model):

    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE
    )

    username = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    district = models.CharField(max_length=100)

    level = models.CharField(max_length=20)

    animal = models.CharField(max_length=100)

    score = models.FloatField()

    won = models.BooleanField()

    ai_cost = models.FloatField()

    questions_used = models.IntegerField()

    wrong_tries = models.IntegerField()

    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.username} - {self.animal}"

# =====================================================
# MONTHLY REWARDS TABLE
# =====================================================

class MonthlyReward(models.Model):

    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE
    )

    reward_type = models.CharField(
        max_length=50
    )

    month = models.IntegerField()

    year = models.IntegerField()

    value = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.player.username} - {self.reward_type}"

# =====================================================
# LEVEL STATISTICS TABLE
# =====================================================

class LevelStats(models.Model):

    player = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE
    )

    level = models.CharField(
        max_length=20
    )

    games_played = models.IntegerField(
        default=0
    )

    total_score = models.FloatField(
        default=0
    )

    max_score = models.FloatField(
        default=0
    )

    average_score = models.FloatField(
        default=0
    )

    def __str__(self):

        return f"{self.player.username} - {self.level}"
