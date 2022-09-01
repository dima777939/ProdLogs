from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from actions.models import Actions
from .models import User, Contact
from orders.models import OrderLog
from .forms import LoginForm, RegistrationForm
from actions.services import ActionUser


class MainView(View):
    def get(self, request):
        actions = []
        if request.user.is_active:
            actions = Actions.objects.exclude(user=request.user)
            following_ids = request.user.following.values_list("id", flat=True)
            if following_ids:
                actions = actions.filter(user_id__in=following_ids)
            actions = actions[:15]
        return render(request, "manufactur/user/main.html", {"actions": actions})


class UserRegisterView(View):
    def get(self, request):
        reg_form = RegistrationForm()
        return render(request, "manufactur/user/register.html", {"reg_form": reg_form})

    def post(self, request):
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            new_user = reg_form.save(commit=False)
            new_user.set_password(reg_form.cleaned_data["password"])
            new_user.save()
            return render(
                request, "manufactur/user/reg_done.html", {"new_user": new_user}
            )
        else:
            return HttpResponse("None")


class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "manufactur/user/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse("manufactur:manufacture"))
            else:
                return HttpResponse("Аккаунт не активен")
        else:
            return render(request, "manufactur/user/login.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class UserListView(View):
    def get(self, request, team=None):
        if team:
            users = User.objects.filter(is_active=True, team=team)
        else:
            users = User.objects.filter(is_active=True)
        return render(request, "manufactur/user/list_user.html", {"users": users})


@method_decorator(login_required, name="dispatch")
class UserDetailView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username, is_active=True)
        orders = OrderLog.objects.filter(operator=user).order_by("-date_finished", "operation", "order__batch_number")
        return render(
            request,
            "manufactur/user/user_detail.html",
            {"user": user, "orders": orders},
        )


@method_decorator(login_required, name="dispatch")
class UserFollowView(View):
    def post(self, request):
        if request.is_ajax():
            user_id = request.POST.get("id")
            action = request.POST.get("action")
            if user_id and action:
                try:
                    user = User.objects.get(id=user_id)
                    if action == "follow":
                        Contact.objects.get_or_create(
                            user_from=request.user, user_to=user
                        )
                        ActionUser(
                            request.user,
                            f"Подписался на {user.first_name} {user.last_name}",
                            "follow",
                            user,
                        ).create_actions()
                    else:
                        Contact.objects.filter(
                            user_from=request.user, user_to=user
                        ).delete()
                    return JsonResponse({"status": "ok"})
                except User.DoesNotExist:
                    return JsonResponse({"status": "ok"})
            return JsonResponse({"status": "ok"})
        return HttpResponse("Запрос принимается только с кнопки 'Подписаться'")
