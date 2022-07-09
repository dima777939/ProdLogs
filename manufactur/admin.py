from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ['team', 'rough_drawing', 'fine_drawing', 'frls', 'yl_300', 'yl_600', 'yl_1250', 'yl_450', 'l_70',
                   'l_90', 'wild_twist', 'twist', 'armoring', 'packaging', 'otk', 'following']