from django.db import models
from django.contrib.auth.models import User
from crm.models import Employee


class HRNote(models.Model):
    """
    HR record attached to an employee.
    Used by the manager to log warnings, commendations,
    performance notes, disciplinary actions, and role changes.
    Employees cannot see these notes.
    """
    NOTE_TYPE_CHOICES = [
        ('warning', 'Written Warning'),
        ('commendation', 'Commendation'),
        ('performance', 'Performance Review'),
        ('disciplinary', 'Disciplinary Action'),
        ('role_change', 'Role / Position Change'),
        ('general', 'General Note'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='hr_notes'
    )
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(
        default=True,
        help_text="Private notes are only visible to the manager, not the employee."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'HR Note'
        verbose_name_plural = 'HR Notes'

    def __str__(self):
        return f"{self.get_note_type_display()} — {self.employee.full_name} ({self.created_at.strftime('%Y-%m-%d')})"
