from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from actions.models import Actions
from .models import User, Contact
from orders.models import OrderLog
from .forms import RegistrationForm
from actions.services import ActionUser


class MainListView(LoginRequiredMixin, ListView):
    template_name = "manufactur/user/main.html"
    paginate_by = 15
    context_object_name = "actions"
    queryset = []

    def get_queryset(self):
        if self.request.user.is_active:
            self.queryset = Actions.objects.exclude(user=self.request.user)
            following_ids = self.request.user.following.values_list("id", flat=True)
            if following_ids:
                self.queryset = self.queryset.filter(user_id__in=following_ids)
            self.queryset = self.queryset.select_related("user").prefetch_related(
                "user__following"
            )[:60]
            return self.queryset


class UserRegisterView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "manufactur.user_add"

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
        return render(request, "manufactur/user/register.html", {"reg_form": reg_form})


class UserListView(LoginRequiredMixin, View):
    def get(self, request, team=None):
        if team:
            users = User.objects.filter(is_active=True, team=team)
        else:
            users = User.objects.filter(is_active=True)
        return render(request, "manufactur/user/list_user.html", {"users": users})


class UserDetailView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username, is_active=True)
        orders = OrderLog.objects.filter(
            operator=user, date_finished__gte=TruncMonth(timezone.now())
        ).order_by("-date_finished")
        return render(
            request,
            "manufactur/user/user_detail.html",
            {"user": user, "orders": orders},
        )


class UserFollowView(LoginRequiredMixin, View):
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
