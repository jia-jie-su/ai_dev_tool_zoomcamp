from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo

# Create your tests here.

class TodoModelTest(TestCase):
    """Test cases for the Todo model"""

    def test_create_todo_with_all_fields(self):
        """Test creating a TODO with all fields"""
        due_date = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title="Test TODO",
            description="Test description",
            due_date=due_date,
            resolved=False
        )
        self.assertEqual(todo.title, "Test TODO")
        self.assertEqual(todo.description, "Test description")
        self.assertEqual(todo.due_date, due_date)
        self.assertFalse(todo.resolved)

    def test_create_todo_with_only_title(self):
        """Test creating a TODO with only required field (title)"""
        todo = Todo.objects.create(title="Minimal TODO")
        self.assertEqual(todo.title, "Minimal TODO")
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.resolved)

    def test_todo_default_resolved_is_false(self):
        """Test that resolved defaults to False"""
        todo = Todo.objects.create(title="Test TODO")
        self.assertFalse(todo.resolved)

    def test_todo_string_representation(self):
        """Test that __str__ returns the title"""
        todo = Todo.objects.create(title="My TODO")
        self.assertEqual(str(todo), "My TODO")

    def test_todo_ordering(self):
        """Test that TODOs are ordered by newest first"""
        todo1 = Todo.objects.create(title="First")
        todo2 = Todo.objects.create(title="Second")
        todo3 = Todo.objects.create(title="Third")

        todos = Todo.objects.all()
        self.assertEqual(todos[0], todo3)  # Newest first
        self.assertEqual(todos[1], todo2)
        self.assertEqual(todos[2], todo1)

    def test_todo_timestamps(self):
        """Test that created_at and updated_at are set"""
        todo = Todo.objects.create(title="Test TODO")
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)


class TodoListViewTest(TestCase):
    """Test cases for the Todo list view"""

    def test_list_view_with_no_todos(self):
        """Test list view when no TODOs exist"""
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No TODOs yet")
        self.assertEqual(len(response.context['todos']), 0)

    def test_list_view_with_todos(self):
        """Test list view displays all TODOs"""
        todo1 = Todo.objects.create(title="TODO 1")
        todo2 = Todo.objects.create(title="TODO 2")

        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TODO 1")
        self.assertContains(response, "TODO 2")
        self.assertEqual(len(response.context['todos']), 2)

    def test_list_view_shows_resolved_status(self):
        """Test that resolved TODOs are displayed differently"""
        todo = Todo.objects.create(title="Resolved TODO", resolved=True)

        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resolved TODO")


class TodoCreateViewTest(TestCase):
    """Test cases for creating TODOs"""

    def test_create_view_get(self):
        """Test GET request shows the create form"""
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New TODO")

    def test_create_todo_with_valid_data(self):
        """Test creating a TODO with valid POST data"""
        data = {
            'title': 'New TODO',
            'description': 'New description',
        }
        response = self.client.post(reverse('todo_create'), data)

        self.assertEqual(Todo.objects.count(), 1)
        todo = Todo.objects.first()
        self.assertEqual(todo.title, 'New TODO')
        self.assertEqual(todo.description, 'New description')
        self.assertRedirects(response, reverse('todo_list'))

    def test_create_todo_without_optional_fields(self):
        """Test creating a TODO without description and due_date"""
        data = {'title': 'Just a title'}
        response = self.client.post(reverse('todo_create'), data)

        self.assertEqual(Todo.objects.count(), 1)
        todo = Todo.objects.first()
        self.assertEqual(todo.title, 'Just a title')
        self.assertEqual(todo.description, '')
        self.assertIsNone(todo.due_date)


class TodoUpdateViewTest(TestCase):
    """Test cases for updating TODOs"""

    def setUp(self):
        """Create a TODO for testing updates"""
        self.todo = Todo.objects.create(
            title="Original Title",
            description="Original description"
        )

    def test_update_view_get(self):
        """Test GET request shows update form with existing data"""
        response = self.client.get(reverse('todo_update', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Original Title")

    def test_update_todo_title(self):
        """Test updating TODO title"""
        data = {
            'title': 'Updated Title',
            'description': self.todo.description,
            'resolved': False
        }
        response = self.client.post(
            reverse('todo_update', args=[self.todo.pk]),
            data
        )

        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title')
        self.assertRedirects(response, reverse('todo_list'))

    def test_update_resolved_status(self):
        """Test updating resolved status"""
        data = {
            'title': self.todo.title,
            'description': self.todo.description,
            'resolved': True
        }
        response = self.client.post(
            reverse('todo_update', args=[self.todo.pk]),
            data
        )

        self.todo.refresh_from_db()
        self.assertTrue(self.todo.resolved)


class TodoDeleteViewTest(TestCase):
    """Test cases for deleting TODOs"""

    def setUp(self):
        """Create a TODO for testing deletion"""
        self.todo = Todo.objects.create(title="TODO to delete")

    def test_delete_view_get(self):
        """Test GET request shows confirmation page"""
        response = self.client.get(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete")
        self.assertContains(response, "TODO to delete")

    def test_delete_todo(self):
        """Test POST request deletes the TODO"""
        response = self.client.post(reverse('todo_delete', args=[self.todo.pk]))

        self.assertEqual(Todo.objects.count(), 0)
        self.assertRedirects(response, reverse('todo_list'))

    def test_delete_nonexistent_todo(self):
        """Test deleting a non-existent TODO returns 404"""
        response = self.client.get(reverse('todo_delete', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TodoToggleResolvedTest(TestCase):
    """Test cases for toggling resolved status"""

    def test_toggle_unresolved_to_resolved(self):
        """Test toggling a TODO from unresolved to resolved"""
        todo = Todo.objects.create(title="Test TODO", resolved=False)

        response = self.client.get(reverse('todo_toggle', args=[todo.pk]))

        todo.refresh_from_db()
        self.assertTrue(todo.resolved)
        self.assertRedirects(response, reverse('todo_list'))

    def test_toggle_resolved_to_unresolved(self):
        """Test toggling a TODO from resolved back to unresolved"""
        todo = Todo.objects.create(title="Test TODO", resolved=True)

        response = self.client.get(reverse('todo_toggle', args=[todo.pk]))

        todo.refresh_from_db()
        self.assertFalse(todo.resolved)
        self.assertRedirects(response, reverse('todo_list'))


class TodoURLTest(TestCase):
    """Test cases for URL routing"""

    def test_list_url_resolves(self):
        """Test that list URL resolves correctly"""
        url = reverse('todo_list')
        self.assertEqual(url, '/')

    def test_create_url_resolves(self):
        """Test that create URL resolves correctly"""
        url = reverse('todo_create')
        self.assertEqual(url, '/create/')

    def test_update_url_resolves(self):
        """Test that update URL resolves correctly"""
        url = reverse('todo_update', args=[1])
        self.assertEqual(url, '/update/1/')

    def test_delete_url_resolves(self):
        """Test that delete URL resolves correctly"""
        url = reverse('todo_delete', args=[1])
        self.assertEqual(url, '/delete/1/')

    def test_toggle_url_resolves(self):
        """Test that toggle URL resolves correctly"""
        url = reverse('todo_toggle', args=[1])
        self.assertEqual(url, '/toggle/1/')
