from django.contrib import admin

from .models import (

    PlayerProfile,

    GameHistory,

    LevelStats,

    MonthlyReward

)

admin.site.register(PlayerProfile)

admin.site.register(GameHistory)

admin.site.register(LevelStats)

admin.site.register(MonthlyReward)
