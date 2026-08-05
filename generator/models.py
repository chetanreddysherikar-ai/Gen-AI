import secrets
import string
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    mobile = models.CharField(max_length=15)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    def __str__(self):
        return self.full_name


class SearchHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    topic = models.CharField(max_length=255)

    generated_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic}"


class EmailOTP(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    email = models.EmailField()

    otp_code = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(default=False)

    attempts = models.IntegerField(default=0)

    def is_valid(self):
        return (not self.is_used) and (timezone.now() <= self.expires_at) and (self.attempts < 3)

    @classmethod
    def generate_otp(cls, email, user=None, validity_minutes=5):
        # Invalidate previous unused OTPs for this email
        cls.objects.filter(email=email, is_used=False).update(is_used=True)

        # Cryptographically secure 6-digit OTP code
        otp = "".join(secrets.choice(string.digits) for _ in range(6))
        expires = timezone.now() + timedelta(minutes=validity_minutes)

        return cls.objects.create(
            user=user,
            email=email,
            otp_code=otp,
            expires_at=expires
        )

    def __str__(self):
        return f"OTP for {self.email} ({'Valid' if self.is_valid() else 'Expired/Used'})"