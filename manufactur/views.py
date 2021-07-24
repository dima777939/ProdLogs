from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import LoginForm, RegistrationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from .models import User


class MainView(View):

    def get(self, request):
        return render(request, 'manufactur/user/main.html')


class UserRegisterView(View):

    def get(self, request):
        reg_form = RegistrationForm()
        return render(request, 'manufactur/user/register.html', {'reg_form': reg_form})

    def post(self, request):
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            new_user = reg_form.save(commit=False)
            new_user.set_password(reg_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'manufactur/user/reg_done.html', {'new_user': new_user})
        else:
            return HttpResponse('None')


class UserLoginView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, 'manufactur/user/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('manufactur:manufacture'))
            else:
                return HttpResponse('Аккаунт не активен')
        else:
            return HttpResponse('Неправильный логин или пароль')


class UserListView(View):

    def get(self, request, team=None):
        if team:
            users = User.objects.filter(is_active=True, team=team)
        else:
            users = User.objects.filter(is_active=True)
        return render(request, 'manufactur/user/list_user.html', {'users': users})

