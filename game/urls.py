from django.urls import path
from . import views

urlpatterns = [

    path('', views.home_view),

    path('login/', views.login_view),

    path('profile/', views.profile_view),

    path('instructions/', views.instructions_view),

    path('game/', views.game_view),

    path('result/', views.result_view),

    path('payment/', views.payment_view),

    path('payment-success/', views.payment_success_view),

    path('logout/', views.logout_view),

    path('setup-profile/', views.setup_profile_view),

    path('monthly-rewards/',views.monthly_rewards_view),

]
