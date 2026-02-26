"""Unit tests for the Sticky Notes application.

These tests exercise the main use cases of the app:

* The Note model and its string representation.
* The NoteForm used for creating and updating notes.
* The function-based views for listing, creating, viewing,
  updating, and deleting notes.
"""

from django.test import TestCase
from django.urls import reverse

from .forms import NoteForm
from .models import Note


class NoteModelTest(TestCase):
    """Tests for the Note model."""

    def setUp(self):
        self.note = Note.objects.create(
            title="Test Note",
            content="This is the content of the test note.",
        )

    def test_note_fields_are_saved_correctly(self):
        """The created note should have the expected title and content."""
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, "Test Note")
        self.assertEqual(note.content, "This is the content of the test note.")

    def test_note_str_returns_title(self):
        """The string representation of a note should be its title."""
        self.assertEqual(str(self.note), "Test Note")

    def test_title_max_length(self):
        """The title field should enforce the configured max_length."""
        max_length = self.note._meta.get_field("title").max_length
        self.assertEqual(max_length, 255)


class NoteFormTest(TestCase):
    """Tests for the NoteForm."""

    def test_form_valid_with_title_and_content(self):
        """A form with both title and content should be valid."""
        form_data = {"title": "Form Note", "content": "Form note body."}
        form = NoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_when_title_missing(self):
        """A form without a title should be invalid."""
        form_data = {"title": "", "content": "Missing title."}
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_invalid_when_content_missing(self):
        """A form without content should be invalid."""
        form_data = {"title": "Missing content", "content": ""}
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)


class NoteViewTests(TestCase):
    """Tests for the note views (list, detail, create, update, delete)."""

    def setUp(self):
        self.note = Note.objects.create(
            title="Initial Note",
            content="Initial note content.",
        )

    def test_note_list_view_status_code_and_template(self):
        """The list view should return HTTP 200 and use the correct template."""
        url = reverse("note_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_list.html")
        self.assertContains(response, "Initial Note")

    def test_note_detail_view_displays_note(self):
        """The detail view should show the selected note."""
        url = reverse("note_detail", args=[self.note.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_detail.html")
        self.assertContains(response, "Initial Note")
        self.assertContains(response, "Initial note content.")

    def test_note_detail_view_404_for_unknown_note(self):
        """Requesting a non-existent note should return 404."""
        url = reverse("note_detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_note_create_view_get_renders_form(self):
        """GET on the create view should render the form."""
        url = reverse("note_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        self.assertIsInstance(response.context["form"], NoteForm)

    def test_note_create_view_valid_post_creates_note(self):
        """A valid POST to the create view should create a new note."""
        url = reverse("note_create")
        data = {"title": "New Note", "content": "New note content."}
        response = self.client.post(url, data)
        # We started with one note in setUp; after creation we expect two.
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.latest("id")
        self.assertEqual(new_note.title, "New Note")
        self.assertEqual(new_note.content, "New note content.")
        self.assertRedirects(response, reverse("note_detail", args=[new_note.pk]))

    def test_note_create_view_invalid_post_shows_errors(self):
        """An invalid POST should re-display the form with errors."""
        url = reverse("note_create")
        data = {"title": "", "content": ""}
        response = self.client.post(url, data)
        # No new note created (still only the one from setUp)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        # Extract the bound form instance from the response context
        form = response.context.get("form")
        self.assertIsNotNone(form, "The response should contain a form in its context.")
        self.assertIsInstance(form, NoteForm)
        # The form should not be valid and should contain field-specific errors
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "title", "This field is required.")
        self.assertFormError(form, "content", "This field is required.")
    def test_note_update_view_get_renders_form(self):
        """GET on the update view should render the form with note data."""
        url = reverse("note_update", args=[self.note.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        form = response.context["form"]
        self.assertIsInstance(form, NoteForm)
        self.assertEqual(form.instance, self.note)

    def test_note_update_view_valid_post_updates_note(self):
        """A valid POST to the update view should save changes."""
        url = reverse("note_update", args=[self.note.pk])
        data = {"title": "Updated Title", "content": "Updated content."}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("note_detail", args=[self.note.pk]))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Updated Title")
        self.assertEqual(self.note.content, "Updated content.")

    def test_note_delete_view_get_confirmation_page(self):
        """GET on the delete view should show a confirmation page."""
        url = reverse("note_delete", args=[self.note.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_confirm_delete.html")
        self.assertContains(response, "Are you sure you want to delete")

    def test_note_delete_view_post_deletes_and_redirects(self):
        """POST to the delete view should delete the note and redirect to the list."""
        url = reverse("note_delete", args=[self.note.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("note_list"))
        self.assertEqual(Note.objects.count(), 0)
