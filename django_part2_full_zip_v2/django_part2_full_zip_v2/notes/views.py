"""Views for the Sticky Notes application.

These views implement basic CRUD operations for notes:
- list notes
- view note detail
- create note
- update note
- delete note
"""

from django.shortcuts import get_object_or_404, redirect, render

from .forms import NoteForm
from .models import Note


def note_list(request):
    """Display a list of all notes."""
    notes = Note.objects.all().order_by("id")
    return render(request, "notes/note_list.html", {"notes": notes})


def note_detail(request, pk):
    """Display the details for a single note."""
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/note_detail.html", {"note": note})


def note_create(request):
    """Create a brand new note.

    On GET: render an empty form.
    On POST: validate and save, then redirect to the detail view.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save()
            return redirect("note_detail", pk=note.pk)
    else:
        form = NoteForm()

    return render(request, "notes/note_form.html", {"form": form})


def note_update(request, pk):
    """Update an existing note.

    On GET: render a form pre-populated with the note data.
    On POST: validate and save changes, then redirect to the detail view.
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            return redirect("note_detail", pk=note.pk)
    else:
        form = NoteForm(instance=note)

    return render(request, "notes/note_form.html", {"form": form})


def note_delete(request, pk):
    """Delete an existing note.

    On GET: show a confirmation page.
    On POST: delete the note and redirect back to the list.
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == "POST":
        note.delete()
        return redirect("note_list")

    return render(request, "notes/note_confirm_delete.html", {"note": note})
