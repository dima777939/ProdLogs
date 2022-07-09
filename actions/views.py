from django.shortcuts import render
from django.views import View

from actions.models import Actions


class ActionsView(View):

    def get(self, request):
        actions = Actions.objects.exclude(user=request.user)
        # actions = Actions.objects.all()
        following_ids = request.user.following.values_list('id', flat=True)
        if following_ids:
            actions = actions.filter(user_id__in=following_ids)
        actions = actions[:15]
        return render(request, 'actions/action_detail.html', {'actions': actions})
        # return render(request, 'manufactur/user/main.html', {'actions': actions})
