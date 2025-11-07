from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pages.models import Vacancy


class Command(BaseCommand):
    help = 'Create sample vacancies for testing'

    def handle(self, *args, **kwargs):
        vacancy = Vacancy.objects.create(
            title='Home Tuition Teacher',
            company_name='CREATIVE EDUCATION FOUNDATION PVT. LTD',
            employment_type='part_time',
            location='Pokhara',
            salary=10000.00,
            level='mid',
            mode='hybrid',
            openings=4,
            start_date=timezone.now().date() + timedelta(days=10),
            deadline=timezone.now().date() + timedelta(days=60),
            description='We are looking for passionate teachers...',
            requirements='Bachelor degree\n1 year experience',
            responsibilities='Conduct tuition\nPrepare materials',
            is_active=True
        )
        self.stdout.write(self.style.SUCCESS(f'Created vacancy: {vacancy.title}'))