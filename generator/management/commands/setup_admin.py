from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from generator.models import UserProfile


class Command(BaseCommand):
    help = "Creates or updates the admin superuser 'chetu' with password '7975474588'."

    def handle(self, *args, **options):
        username = "chetu"
        password = "7975474588"
        email = "chetangowda7975@gmail.com"

        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        # Ensure UserProfile exists
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": "Chetu Admin",
                "email": email,
                "mobile": "7975474588",
                "gender": "Male",
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully created superuser '{username}' with specified password."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully updated superuser '{username}' password and admin permissions."))
