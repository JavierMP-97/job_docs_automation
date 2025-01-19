from calendar import c
import copy
from email.policy import HTTP
from typing import Optional

from django.http import HttpRequest

from backend import execute_step, read_files, save_to_docx
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CoverLetter, Profile

inputs, prompts = read_files(input_filenames="inputs.txt", prompt_filenames="prompts_2.txt")


def create_session(request) -> None:
    request.session["current_step"] = 0
    request.session["replacements"] = copy.copy(inputs)
    request.session["last_step_options"] = []
    request.session["current_option_idx"] = 0


def check_session_expired(request) -> Optional[Response]:
    if (
        "current_step" not in request.session
        or "replacements" not in request.session
        or "last_step_options" not in request.session
        or "current_option_idx" not in request.session
    ):
        # Return a error response according to rest framework
        return Response(data={"content": "Error: Session expired."}, status=400)


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
    create_session(request)
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
def generate_step_cover_letter(request) -> Response:
    return handle_cover_letter_step(request)


@login_required
@api_view(["POST"])
def left_step(request) -> Response:
    return change_step_option(request, left=True)


@login_required
@api_view(["POST"])
def right_step(request) -> Response:
    return change_step_option(request, left=False)


def handle_cover_letter_step(request) -> Response:
    session_expired = check_session_expired(request)
    if session_expired:
        return session_expired
    if "retry" in request.data:
        if "job_description" in request.data or request.session["current_step"] <= 0:
            return Response({"content": "Error: How did you get here?"})
        request.session["current_step"] -= 1
    if "job_description" in request.data:
        if request.session["current_step"] > 0:
            return Response({"content": "Error: How did you get here?"})

        request.session["replacements"]["job_description"] = request.data["job_description"]

    replacements = request.session["replacements"]
    current_step = request.session["current_step"]

    generated_text = execute_step(step=current_step, prompts=prompts, replacements=replacements)

    if not "retry" in request.data:
        request.session["last_step_options"] = []
    request.session["current_option_idx"] = len(request.session["last_step_options"])
    request.session["last_step_options"].append(generated_text)

    if generated_text is None:
        # Return an error message if the completion fails
        return Response({"content": "Error: Completion failed."})

    # Check if all steps are completed
    if current_step >= len(prompts):
        return Response({"content": "All steps are completed!"})

    request.session["current_step"] += 1

    response = render_step_html(
        request=request,
        content=generated_text,
    )

    return Response({"content": response})


def change_step_option(request, left: bool = False) -> Response:
    session_expired = check_session_expired(request)
    if session_expired:
        return session_expired
    if left:
        if request.session["current_option_idx"] > 0:
            request.session["current_option_idx"] -= 1
        else:
            return Response({"content": "Error: How did you get here?"})
    else:
        if request.session["current_option_idx"] < len(request.session["last_step_options"]) - 1:
            request.session["current_option_idx"] += 1
        else:
            return Response({"content": "Error: How did you get here?"})
    prev_step = request.session["current_step"] - 1
    prev_step_name = prompts[prev_step][0]
    content = request.session["last_step_options"][request.session["current_option_idx"]]
    request.session["replacements"][prev_step_name] = content

    response = render_step_html(
        request=request,
        content=content,
    )

    return Response({"content": response})


def render_step_html(request: HttpRequest, content: str):
    """
    Renders the step HTML using the provided data.

    Parameters
    ----------
    request : HttpRequest
        The request object.
    content : str
        The content for the current step.

    Returns
    -------
    str
        The rendered HTML as a string.
    """

    context = {
        "prev_step": prompts[request.session["current_step"] - 1].name,
        "content": content,
        "left_button": request.session["current_option_idx"] > 0,
        "right_button": request.session["current_option_idx"]
        < len(request.session["last_step_options"]) - 1,
        "next_step": (
            prompts[request.session["current_step"]].name
            if request.session["current_step"] < len(prompts)
            else None
        ),
    }
    return render_to_string("jda/dynamic_section_template.html", context)


@login_required
@api_view(["POST"])
def save_step(request):
    session_expired = check_session_expired(request)
    if session_expired:
        return session_expired
    last_prompt_name = prompts[request.session["current_step"] - 1][0]
    save_to_docx(
        content=request.session["replacements"][last_prompt_name],
        output_file="cover_letter.docx",
    )
    return Response({}, status=200)
