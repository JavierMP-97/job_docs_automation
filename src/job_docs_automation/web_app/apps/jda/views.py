from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view


from .models import CoverLetter, Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.experience = request.POST.get("experience", "")
        profile.education = request.POST.get("education", "")
        profile.save()
        return redirect("/profile/")
    return render(request, "profile.html", {"profile": profile})


@login_required
def generate_cover_letter(request):
    if request.method == "POST":
        # Placeholder: Your step-by-step logic here
        # `step` and `content` should handle the sequence and display output
        return redirect("/cover-letters/")
    return render(request, "jda/generate_cover_letter.html")


@login_required
def list_cover_letters(request):
    letters = CoverLetter.objects.filter(user=request.user)
    return render(request, "cover_letters.html", {"letters": letters})


@login_required
def edit_cover_letter(request, pk):
    letter = get_object_or_404(CoverLetter, id=pk, user=request.user)
    if request.method == "POST":
        letter.content = request.POST.get("content", letter.content)
        letter.save()
        return redirect("/cover-letters/")
    return render(request, "edit_cover_letter.html", {"letter": letter})


@api_view(["GET"])
def login_page(request):
    user = request.user
    if user.is_authenticated:
        return render(request, "jda/generate_cover_letter.html")
    return render(request, "jda/login_page.html")
