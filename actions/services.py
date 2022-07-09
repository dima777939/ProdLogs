import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Actions


class ActionUser:

    def __init__(self, user, verb, type_target=None, target=None):
        self.user = user
        self.verb = verb
        self.type_target = type_target
        self.target = target

    def create_actions(self):
        now = timezone.now()
        last_minute = now - datetime.timedelta(seconds=60)
        similar_action = Actions.objects.filter(user_id=self.user.id, verb=self.verb, type_target=self.type_target, created__gte=last_minute)
        if self.target:
            target_ct = ContentType.objects.get_for_model(self.target)
            similar_action = similar_action.filter(target_ct=target_ct, target_id=self.target.id)
        if not similar_action:
            action = Actions(user=self.user, verb=self.verb, type_target=self.type_target, target=self.target)
            action.save()
        return False
