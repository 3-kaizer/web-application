#!/usr/bin/env python3
"""
Automated script to create a Django superuser.
Run with: python3 create_superuser.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_lux.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    username = 'zake'
    email = 'zake@audiolux.com'
    password = '510840'

    if User.objects.filter(username=username).exists():
        print(f'Superuser "{username}" already exists. Skipping creation.')
        return

    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()

    print('=' * 50)
    print('Superuser created successfully!')
    print('=' * 50)
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'Email: {email}')
    print('=' * 50)
    print('You can now log in at: http://127.0.0.1:8000/admin/')
    print('=' * 50)

if __name__ == '__main__':
    create_superuser()