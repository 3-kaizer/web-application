#!/usr/bin/env python3
"""
Complete setup script for Audio Lux e-commerce project.
Runs database migrations, populates initial products, and creates superuser.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_lux.settings')
django.setup()

import sys
from django.core.management import call_command
from django.contrib.auth import get_user_model

def run_migrations():
    print('Running database migrations...')
    call_command('migrate', verbosity=2)
    print()

def populate_products():
    print('Populating products...')
    call_command('populate_products', verbosity=2)
    print()

def create_superuser():
    User = get_user_model()
    username = 'zake'
    email = 'zake@audiolux.com'
    password = '510840'

    if User.objects.filter(username=username).exists():
        print(f'Superuser "{username}" already exists. Skipping creation.')
    else:
        call_command('createsuperuser', username=username, email=email)
        # Set password
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f'Superuser configured: username={username}, password={password}')

def main():
    print('=' * 60)
    print('Audio Lux - Complete Setup')
    print('=' * 60)
    print()

    run_migrations()
    populate_products()
    create_superuser()

    print()
    print('=' * 60)
    print('Setup completed successfully!')
    print('=' * 60)
    print('Access admin at: http://127.0.0.1:8000/admin/')
    print('Username: zake | Password: 510840')
    print('Visit site at: http://127.0.0.1:8000/')
    print('=' * 60)

if __name__ == '__main__':
    main()