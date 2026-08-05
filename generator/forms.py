from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class TopicForm(forms.Form):

    topic = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter your topic..."
            }
        )
    )


class RegisterForm(forms.ModelForm):

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    mobile = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "email",
            "mobile",
            "gender",
        ]

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


# --- Admin Panel Forms ---

class AdminUserCreateForm(forms.Form):
    """Used by admins to create a brand-new user + profile from the admin panel."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    mobile = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    is_staff = forms.BooleanField(
        required=False,
        label="Grant admin panel access",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Active account",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class AdminUserEditForm(forms.ModelForm):
    """Used by admins to edit an existing user's account + profile together."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Leave blank to keep current password"
        })
    )

    is_staff = forms.BooleanField(
        required=False,
        label="Admin panel access",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    is_active = forms.BooleanField(
        required=False,
        label="Active account",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = UserProfile
        fields = ["full_name", "email", "mobile", "gender"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "mobile": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)
        if self.user_instance:
            qs = qs.exclude(id=self.user_instance.id)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username