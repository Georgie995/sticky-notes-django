"""Forms for creating and updating notes."""

from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    """ModelForm used for note create/update views."""

    class Meta:
        model = Note
        fields = ["title", "content"]
