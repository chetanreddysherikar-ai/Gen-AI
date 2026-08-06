import os
import uuid
import re
import PyPDF2  # <-- Added for reading uploaded PDFs
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

import markdown
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from dotenv import load_dotenv
from google import genai
from gtts import gTTS

from .forms import AdminUserCreateForm, AdminUserEditForm, RegisterForm, TopicForm
from .models import SearchHistory, UserProfile, EmailOTP

# Load environment variables (.env)
load_dotenv()

# Read API Key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key) if api_key else None


def generate_text(topic):
    """Call the Gemini API and return nicely structured Markdown content."""

    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to your .env file."
        )

    prompt = f"""
You are a professional content writer.

Write about: {topic}

IMPORTANT RULES:
1. Return the answer ONLY in Markdown.
2. Do NOT write long paragraphs.
3. Every section must contain bullet points.
4. Each bullet should be 1-2 lines only.
5. Use "-" for bullets.
6. Use proper Markdown headings.

Use this exact format:

# {topic}

## Introduction
- Point 1
- Point 2
- Point 3

## Key Features
- Feature 1
- Feature 2
- Feature 3
- Feature 4

## Advantages
- Advantage 1
- Advantage 2
- Advantage 3
- Advantage 4

## Applications
- Application 1
- Application 2
- Application 3
- Application 4

## Career Opportunities
- Opportunity 1
- Opportunity 2
- Opportunity 3

## Conclusion
- Summary point 1
- Summary point 2

Do not write paragraphs.
Do not add any extra text outside this structure.
"""

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    last_error = None
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                import time
                time.sleep(0.5)

    if last_error:
        raise last_error
    raise RuntimeError("Service temporarily busy. Please try again in a few seconds.")



def home(request):
    generated_html = ""
    raw_text = ""
    audio_url = ""
    form = TopicForm()
    topic = ""

    if request.method == "POST":
        form = TopicForm(request.POST)

        if form.is_valid():
            topic = form.cleaned_data["topic"]
            
            try:
                # Generate AI text via Gemini API
                raw_text = generate_text(topic)

                if raw_text and raw_text.strip():
                    # Convert Markdown to HTML
                    generated_html = markdown.markdown(
                        raw_text,
                        extensions=["extra"]
                    )

                    # Generate optional TTS audio narration safely
                    try:
                        clean_text = re.sub(r'[#*\-`]', '', raw_text).strip()
                        if clean_text:
                            # Use first 300 characters for audio generation to prevent rate limits
                            tts = gTTS(text=clean_text[:300], lang="en")
                            filename = f"{uuid.uuid4()}.mp3"
                            audio_path = os.path.join(
                                settings.MEDIA_ROOT,
                                "audio",
                                filename
                            )
                            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                            tts.save(audio_path)
                            audio_url = settings.MEDIA_URL + "audio/" + filename
                    except Exception:
                        audio_url = ""

            except Exception as e:
                generated_html = f"<p class='text-danger'>⚠️ {e}</p>"

    return render(request, "home.html", {
        "form": form,
        "topic": topic,
        "raw_text": raw_text,
        "generated_text": generated_html,
        "audio_url": audio_url,
    })



# --- Authentication & User Views ---

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=username).exists():
                form.add_error("username", "This username is already taken.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data["email"],
                    password=password,
                )
                user_profile = form.save(commit=False)
                user_profile.user = user
                user_profile.save()

                login(request, user)
                messages.success(request, f"Welcome, {user_profile.full_name}! Your account was created successfully.")
                return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def request_otp(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email_or_username = request.POST.get("email_or_username", "").strip()
        if not email_or_username:
            messages.error(request, "Please enter your registered email address or username.")
            return render(request, "request_otp.html")

        # Search for user by username or email
        user = User.objects.filter(Q(email__iexact=email_or_username) | Q(username__iexact=email_or_username)).first()

        if not user:
            profile = UserProfile.objects.filter(email__iexact=email_or_username).first()
            if profile:
                user = profile.user

        if not user:
            messages.error(request, "No account found with that email or username. Please register first.")
            return render(request, "request_otp.html", {"email_or_username": email_or_username})

        target_email = user.email
        if not target_email and hasattr(user, 'userprofile'):
            target_email = user.userprofile.email

        if not target_email:
            messages.error(request, "No valid email address found for this user.")
            return render(request, "request_otp.html")

        # Generate 6-digit secure OTP
        otp_obj = EmailOTP.generate_otp(email=target_email, user=user)

        # Send Email via SMTP
        subject = "Your Security OTP Code - AI Text Generator"
        message_body = (
            f"Hello {user.username},\n\n"
            f"Your One-Time Password (OTP) for login is: {otp_obj.otp_code}\n\n"
            f"This code is valid for 5 minutes. Please do not share this OTP with anyone.\n\n"
            f"If you did not request this OTP, please ignore this email.\n\n"
            f"Regards,\nAI Text Generator Security Team"
        )

        try:
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[target_email],
                fail_silently=False,
            )
            request.session["otp_target_email"] = target_email
            messages.success(request, f"OTP has been sent to {target_email}. Please check your inbox.")
            return redirect("verify_otp")
        except Exception as e:
            messages.error(request, f"Failed to send email OTP: {e}")
            return render(request, "request_otp.html", {"email_or_username": email_or_username})

    return render(request, "request_otp.html")


def verify_otp(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    target_email = request.session.get("otp_target_email", "")

    if request.method == "POST":
        otp_code = request.POST.get("otp_code", "").strip()
        email = request.POST.get("email", target_email).strip()

        if not email or not otp_code:
            messages.error(request, "Please enter both your email address and 6-digit OTP code.")
            return render(request, "verify_otp.html", {"email": email})

        otp_record = EmailOTP.objects.filter(email__iexact=email, is_used=False).order_by("-created_at").first()

        if not otp_record:
            messages.error(request, "No active OTP request found for this email. Please request a new OTP.")
            return redirect("request_otp")

        if not otp_record.is_valid():
            messages.error(request, "This OTP has expired or exceeded maximum attempt limits. Please request a new OTP.")
            return redirect("request_otp")

        if otp_record.otp_code != otp_code:
            otp_record.attempts += 1
            otp_record.save()
            remaining = 3 - otp_record.attempts
            if remaining > 0:
                messages.error(request, f"Invalid OTP code. You have {remaining} attempt(s) left.")
            else:
                messages.error(request, "Invalid OTP code. Attempt limit reached. Please request a new OTP.")
                return redirect("request_otp")
            return render(request, "verify_otp.html", {"email": email})

        # OTP match!
        otp_record.is_used = True
        otp_record.save()

        user = otp_record.user
        if not user:
            user = User.objects.filter(email__iexact=email).first()

        if user:
            login(request, user)
            if "otp_target_email" in request.session:
                del request.session["otp_target_email"]
            messages.success(request, f"Authentication successful! Welcome back, {user.username}.")
            return redirect("dashboard")
        else:
            messages.error(request, "User account not found.")
            return redirect("login")

    return render(request, "verify_otp.html", {"email": target_email})



@login_required
def dashboard(request):
    generated_text = ""
    raw_text = ""
    topic = ""

    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()
        if not topic:
            messages.error(request, "Please enter a topic to generate content.")
        else:
            try:
                raw_text = generate_text(topic)
                generated_text = markdown.markdown(raw_text, extensions=["extra"])
                SearchHistory.objects.create(
                    user=request.user,
                    topic=topic,
                    generated_text=raw_text,
                )
            except Exception as e:
                generated_text = f"<p class='text-danger mb-0'>⚠️ {e}</p>"

    history = SearchHistory.objects.filter(user=request.user).order_by("-created_at")[:10]

    return render(request, "dashboard.html", {
        "topic": topic,
        "raw_text": raw_text,
        "generated_text": generated_text,
        "history": history,
    })


@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or f"{request.user.username}@example.com",
            "mobile": "",
            "gender": "Other",
        },
    )
    return render(request, "profile.html", {"profile": user_profile})


def text_to_audio(request):
    text = ""
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
    return render(request, "text_to_audio.html", {"text": text})



@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


# --- PDF Generation View ---

def download_pdf(request):
    """Takes generated raw markdown text via POST and converts it to a downloadable PDF"""
    if request.method == "POST":
        topic = request.POST.get("topic", "Generated_Document")
        raw_text = request.POST.get("raw_text", "")

        # Format the filename safely
        safe_filename = "".join([c for c in topic if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_filename = safe_filename.replace(" ", "_")
        if not safe_filename:
            safe_filename = "document"

        # Create the HttpResponse object with the appropriate PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}.pdf"'

        # Setup ReportLab Document
        doc = SimpleDocTemplate(response)
        styles = getSampleStyleSheet()
        elements = []

        # Parse the Markdown text and convert to ReportLab Paragraphs
        for line in raw_text.split('\n'):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 10))
                continue
            
            # Basic markdown bold text parser for ReportLab (replace **text** with <b>text</b>)
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)

            if line.startswith('# '):
                elements.append(Paragraph(line[2:], styles['Heading1']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], styles['Heading2']))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], styles['Heading3']))
            elif line.startswith('- ') or line.startswith('* '):
                elements.append(Paragraph(line, styles['Bullet']))
            else:
                elements.append(Paragraph(line, styles['Normal']))

        # Build the PDF and write to response
        doc.build(elements)
        return response

    # If accessed via GET, redirect back to home
    return redirect("home")



# --- NEW: Google Maps Route View ---

def map_route(request):
    """Serves the page for detecting location and getting Google Maps routes."""
    return render(request, "map.html")


# =========================================================
#  ADMIN PANEL  — full CRUD control over users & history
#  Only accessible to staff/superuser accounts.
# =========================================================

def admin_required(view_func):
    """Restrict a view to logged-in staff/superuser accounts."""
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url="login",
    )(view_func)


@admin_required
def admin_dashboard(request):
    """Overview stats + quick links for the site admin."""

    stats = {
        "total_users": User.objects.count(),
        "total_staff": User.objects.filter(is_staff=True).count(),
        "total_active": User.objects.filter(is_active=True).count(),
        "total_history": SearchHistory.objects.count(),
    }

    recent_users = User.objects.select_related("userprofile").order_by("-date_joined")[:6]
    recent_history = SearchHistory.objects.select_related("user").order_by("-created_at")[:6]

    return render(request, "admin_panel/dashboard.html", {
        "stats": stats,
        "recent_users": recent_users,
        "recent_history": recent_history,
        "active": "dashboard",
    })


@admin_required
def admin_user_list(request):
    """List every user with search + pagination, entry point for CRUD."""

    query = request.GET.get("q", "").strip()
    users = User.objects.select_related("userprofile").order_by("-date_joined")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(userprofile__full_name__icontains=query)
        )

    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "admin_panel/user_list.html", {
        "page_obj": page_obj,
        "query": query,
        "active": "users",
    })


@admin_required
def admin_user_add(request):
    """Create a brand-new user + profile from the admin panel."""

    if request.method == "POST":
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                is_staff=form.cleaned_data["is_staff"],
                is_active=form.cleaned_data["is_active"],
            )
            UserProfile.objects.create(
                user=new_user,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                mobile=form.cleaned_data["mobile"],
                gender=form.cleaned_data["gender"],
            )
            messages.success(request, f"User '{new_user.username}' created successfully.")
            return redirect("admin_users")
    else:
        form = AdminUserCreateForm()

    return render(request, "admin_panel/user_form.html", {"form": form, "mode": "add", "active": "users"})


@admin_required
def admin_user_edit(request, user_id):
    """Edit any user's account details + profile in one form."""

    target_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(
        user=target_user,
        defaults={
            "full_name": target_user.get_full_name() or target_user.username,
            "email": target_user.email or f"{target_user.username}@example.com",
            "mobile": "",
            "gender": "Other",
        },
    )

    if request.method == "POST":
        form = AdminUserEditForm(request.POST, instance=profile, user_instance=target_user)
        if form.is_valid():
            target_user.username = form.cleaned_data["username"]
            target_user.email = form.cleaned_data["email"]
            target_user.is_active = form.cleaned_data["is_active"]
            target_user.is_staff = form.cleaned_data["is_staff"]

            new_password = form.cleaned_data.get("new_password")
            if new_password:
                target_user.set_password(new_password)

            target_user.save()

            saved_profile = form.save(commit=False)
            saved_profile.user = target_user
            saved_profile.save()

            messages.success(request, f"User '{target_user.username}' updated successfully.")
            return redirect("admin_users")
    else:
        form = AdminUserEditForm(
            instance=profile,
            user_instance=target_user,
            initial={
                "username": target_user.username,
                "email": target_user.email,
                "is_active": target_user.is_active,
                "is_staff": target_user.is_staff,
            },
        )

    return render(request, "admin_panel/user_form.html", {
        "form": form,
        "mode": "edit",
        "target_user": target_user,
        "active": "users",
    })


@admin_required
def admin_user_delete(request, user_id):
    """Delete a user account (and cascade their profile/history)."""

    target_user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        if target_user == request.user:
            messages.error(request, "You cannot delete the account you are currently logged in as.")
        else:
            username = target_user.username
            target_user.delete()
            messages.success(request, f"User '{username}' was deleted.")
        return redirect("admin_users")

    return render(request, "admin_panel/confirm_delete.html", {
        "title": "Delete user",
        "object_label": target_user.username,
        "warning": "This permanently deletes the account, its profile, and its search history.",
        "cancel_url": "admin_users",
        "active": "users",
    })


@admin_required
def admin_history_list(request):
    """List every user's generated-content history with search + pagination."""

    query = request.GET.get("q", "").strip()
    history = SearchHistory.objects.select_related("user").order_by("-created_at")

    if query:
        history = history.filter(
            Q(topic__icontains=query) | Q(user__username__icontains=query)
        )

    paginator = Paginator(history, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "admin_panel/history_list.html", {
        "page_obj": page_obj,
        "query": query,
        "active": "history",
    })


@admin_required
def admin_history_detail(request, history_id):
    """View the full generated text for one history entry."""

    item = get_object_or_404(SearchHistory.objects.select_related("user"), id=history_id)
    rendered = markdown.markdown(item.generated_text, extensions=["extra"])

    return render(request, "admin_panel/history_detail.html", {
        "item": item,
        "rendered": rendered,
        "active": "history",
    })


@admin_required
def admin_history_delete(request, history_id):
    """Delete one search-history entry."""

    item = get_object_or_404(SearchHistory, id=history_id)

    if request.method == "POST":
        topic = item.topic
        item.delete()
        messages.success(request, f"Entry '{topic}' was deleted.")
        return redirect("admin_history")

    return render(request, "admin_panel/confirm_delete.html", {
        "title": "Delete history entry",
        "object_label": item.topic,
        "warning": "This permanently removes the generated content record.",
        "cancel_url": "admin_history",
        "active": "history",
    })
    
# --- NEW: PDF Reader View ---

def read_pdf(request):
    """Handles PDF file upload, extracts text, and generates audio."""
    extracted_text = ""
    audio_url = ""

    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        
        try:
            # 1. Read the PDF and extract text
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + " "
            
            clean_text = extracted_text.strip()
            
            # 2. Check if text was found
            if not clean_text:
                messages.error(request, "No readable text found in this PDF. It might be an image-based PDF.")
            else:
                # 3. Convert extracted text to Speech (gTTS)
                tts = gTTS(text=clean_text, lang="en")
                filename = f"pdf_audio_{uuid.uuid4()}.mp3"
                
                audio_path = os.path.join(
                    settings.MEDIA_ROOT,
                    "audio",
                    filename
                )
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                
                # Save audio
                tts.save(audio_path)
                audio_url = settings.MEDIA_URL + "audio/" + filename
                
                messages.success(request, "PDF processed successfully! You can now listen to it.")
                
        except Exception as e:
            messages.error(request, f"Error processing PDF: {e}")

    return render(request, "read_pdf.html", {
        "extracted_text": extracted_text,
        "audio_url": audio_url,
    })