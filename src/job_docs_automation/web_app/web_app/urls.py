"""
URL configuration for web_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from apps.jda.views import (
    edit_cover_letter,
    generate_cover_letter,
    generate_step_cover_letter,
    left_step,
    list_cover_letters,
    login_page,
    profile_view,
    right_step,
    save_step,
)
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', generate_cover_letter, name='generate_cover_letter'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # For Google/Facebook auth
    path('profile/', profile_view, name='profile'),
    path('cover-letters/', list_cover_letters, name='cover_letters'),
    path('generate_cover_letter/', generate_cover_letter, name='generate_cover_letter'),
    path('generate-step/', generate_step_cover_letter, name='generate_step_cover_letter'),
    path('left-step/', left_step, name='left_step'),
    path('right-step/', right_step, name='right_step'),
    path('save-step/', save_step, name='save_step'),
    path('cover-letters/edit/<int:pk>/', edit_cover_letter, name='edit_cover_letter'),
    path('login_page/', login_page, name='login_page'),
]
