from django.core.management.base import BaseCommand
from algosite.models import Topic

class Command(BaseCommand):
    help = 'Загрузить изначальные темы олимпиадного программирования'

    def handle(self, *args, **options):
        topics_data = [
            {
                'slug': 'bfs',
                'title': 'BFS (Поиск в ширину)',
                'explanation': '''Поиск в ширину (BFS) — это алгоритм...''',
                'example_code': '''#include <iostream> ...''',
            },
            {
                'slug': 'lca',
                'title': 'LCA (Нижний общий предок)',
                'explanation': '''Нижний общий предок (LCA)...''',
                'example_code': '''#include <bits/stdc++.h> ...''',
            },
        ]

        for data in topics_data:
            topic, created = Topic.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'title': data['title'],
                    'explanation': data['explanation'],
                    'example_code': data['example_code'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создана тема: {topic.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Обновлена тема: {topic.title}"))
