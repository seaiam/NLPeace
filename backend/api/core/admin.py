from django.contrib import admin
from django.contrib.auth.models import User

from core.models.models import Post, PostReport, Profile

class ProfileInline(admin.TabularInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    inlines = [ProfileInline]

@admin.action(description='Incorporate with NLP model')
def send_to_nlp(modeladmin, request, queryset):
    # TODO implement this once NLP integration has been performed
    pass

class PostReportAdmin(admin.ModelAdmin):
    model = PostReport
    actions = [send_to_nlp]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(PostReport, PostReportAdmin)
