#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_lux.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Customer

User = get_user_model()

username = 'manager'
email = 'manager@audiolux.com'
password = '510840'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    Customer.objects.get_or_create(
        user=user,
        defaults={'email': email}
    )
    print(f'Superuser "{username}" created successfully!')
else:
    print(f'Superuser "{username}" already exists.')