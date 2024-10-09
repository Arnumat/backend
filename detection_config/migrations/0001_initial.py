# Generated by Django 5.0.6 on 2024-10-09 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DetectionConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_start', models.TimeField()),
                ('time_end', models.TimeField()),
                ('sequence_notify', models.IntegerField()),
                ('sequence_insert_data', models.IntegerField()),
            ],
        ),
    ]
