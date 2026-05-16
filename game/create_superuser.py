from django.contrib.auth.models import User

from django.conf import settings


def create_superuser():

    if not User.objects.filter(

        username=settings.DJANGO_SUPERUSER_USERNAME

    ).exists():

        User.objects.create_superuser(

            settings.DJANGO_SUPERUSER_USERNAME,

            settings.DJANGO_SUPERUSER_EMAIL,

            settings.DJANGO_SUPERUSER_PASSWORD

        )
