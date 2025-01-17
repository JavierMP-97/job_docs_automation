import copy
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend import read_files, execute_step

from .models import CoverLetter, Profile

initial_prompt, inputs, prompts = read_files()


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
    if "current_step" in request.session:
        del request.session["current_step"]
    if "replacements" in request.session:
        del request.session["replacements"]
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


@login_required
@api_view(["POST"])
def next_step_cover_letter(request) -> Response:
    return handle_cover_letter_step(request)


def handle_cover_letter_step(request) -> Response:
    if "retry" in request.data:
        if (
            "job_description" in request.data
            or "current_step" not in request.session
            or "replacements" not in request.session
            or request.session["current_step"] <= 0
        ):
            return Response({"content": "Error: How did you get here?", "next_step": None})
        request.session["current_step"] -= 1
    if "job_description" in request.data:
        if (
            "current_step" in request.session
            or "replacements" in request.session
            or "retry" in request.data
        ):
            return Response({"content": "Error: How did you get here?", "next_step": None})
        request.session["current_step"] = 0
        request.session["replacements"] = copy.deepcopy(inputs)
        request.session["replacements"]["job_description"] = request.data["job_description"]

    if "current_step" not in request.session or "replacements" not in request.session:
        return Response({"content": "Error: Session expired.", "next_step": None})

    replacements = request.session["replacements"]
    current_step = request.session["current_step"]

    generated_text = execute_step(
        step=current_step, initial_prompt=initial_prompt, prompts=prompts, replacements=replacements
    )
    if generated_text is None:
        # Return an error message if the completion fails
        return Response({"content": "Error: Completion failed.", "next_step": None})

    # Check if all steps are completed
    if current_step >= len(prompts):
        request.session.flush()  # Clear the session
        return Response({"content": "All steps are completed!", "next_step": None})

    request.session["current_step"] += 1

    response = {
        "content": generated_text,
        "prev_step": prompts[current_step][0],
    }

    if request.session["current_step"] < len(prompts):
        response["next_step"] = prompts[request.session["current_step"]][0]

    return Response(response)
