from typing import Any, Iterator, Optional
from django.contrib import admin
from django.contrib.auth.models import User
from django.http.request import HttpRequest

from core.models.models import Post, PostReport, Profile, ProfileWarning, UserReport

class ProfileInline(admin.TabularInline):
    model = Profile
    fields = ['bio', 'banner', 'pic', 'is_private']

class ProfileWarningInline(admin.StackedInline):
    model = ProfileWarning
    verbose_name = 'Warning'
    verbose_name_plural = 'Warnings'
    extra = 0
    fields = ['note']
    fk_name = 'offender'

class UserAdmin(admin.ModelAdmin):
    model = User
    inlines = [ProfileInline, ProfileWarningInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, ProfileWarning):
                instance.issuer = request.user
            instance.save()
        formset.save_m2m()

@admin.action(description='Incorporate with NLP model')
def send_to_nlp(modeladmin, request, queryset):
    # TODO implement this once NLP integration has been performed
    pass

class PostReportAdmin(admin.ModelAdmin):
    model = PostReport
    actions = [send_to_nlp]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserReport)
admin.site.register(Post)
admin.site.register(PostReport, PostReportAdmin)
