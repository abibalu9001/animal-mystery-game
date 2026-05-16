from django.contrib import admin

from .models import (

    PlayerProfile,

    GameHistory,

    LevelStats,

    MonthlyReward

)


# =====================================================
# PLAYER PROFILE ADMIN
# =====================================================

@admin.register(PlayerProfile)

class PlayerProfileAdmin(admin.ModelAdmin):

    list_display = (

        "id",

        "username",

        "email",

        "state",

        "district",

        "total_games_played",

        "max_score",

        "total_average_score",

        "remaining_games"

    )

    search_fields = (

        "username",

        "email",

        "state",

        "district"

    )


# =====================================================
# GAME HISTORY ADMIN
# =====================================================

@admin.register(GameHistory)

class GameHistoryAdmin(admin.ModelAdmin):

    list_display = (

        "id",

        "username",

        "level",

        "animal",

        "score",

        "won",

        "ai_cost",

        "questions_used",

        "wrong_tries",

        "played_at"

    )

    search_fields = (

        "username",

        "animal",

        "level"

    )


# =====================================================
# LEVEL STATS ADMIN
# =====================================================

@admin.register(LevelStats)

class LevelStatsAdmin(admin.ModelAdmin):

    list_display = (

        "id",

        "player",

        "level",

        "games_played",

        "average_score",

        "max_score"

    )

    search_fields = (

        "player__username",

        "level"

    )


# =====================================================
# MONTHLY REWARD ADMIN
# =====================================================

@admin.register(MonthlyReward)

class MonthlyRewardAdmin(admin.ModelAdmin):

    list_display = (

        "id",

        "player",

        "reward_type",

        "month",

        "year",

        "value"

    )

    search_fields = (

        "player__username",

        "reward_type"

    )
