from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """
    This command init user for using it for logging in service
    """

    def handle(self, *args, **options):
        email = 'admin@acme.test'
        password = '123'
        user, created = User.objects.get_or_create(username=email, email=email)
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(
            'Added initial user. For log in to service use that creds: '
            '`{}` / `{}`'.format(email, password)
        ))
