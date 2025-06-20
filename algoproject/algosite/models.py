from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Topic(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    example_code = models.TextField()

    exercise_render_code = models.TextField(
        blank=True, null=True
    )
    exercise_logic_code = models.TextField(
        blank=True, null=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class TopicRequest(models.Model):
    title = models.CharField(max_length=200)
    explanation = models.TextField(blank=True, null=True)
    example_code = models.TextField(blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    exercise_render_code = models.TextField(
        blank=True, null=True
    )
    exercise_logic_code = models.TextField(
        blank=True, null=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title