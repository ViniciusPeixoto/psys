# Generated by Django 5.0.6 on 2024-06-29 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trees', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='joined',
        ),
    ]