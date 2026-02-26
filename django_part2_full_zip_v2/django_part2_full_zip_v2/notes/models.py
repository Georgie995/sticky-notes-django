"""Database models for the Sticky Notes application.

This app stores simple notes with a title and body content.
"""

from django.db import models


class Note(models.Model):
    """A single sticky note."""

    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self) -> str:
        """Return a human-readable label for the note."""
        return self.title
