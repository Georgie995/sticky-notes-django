"""Admin configuration for the notes app."""

from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin options for Note objects."""

    list_display = ("id", "title")
    search_fields = ("title",)
