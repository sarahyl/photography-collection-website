# Generated by Django 5.0.1 on 2024-06-07 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0011_contest_contestsubmission'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='description',
            field=models.TextField(default=''),
        ),
    ]