# Generated by Django 5.0.6 on 2024-09-28 13:58

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FrameDetection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/detected')),
                ('snail_detected', models.IntegerField()),
                ('time_detect', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='LandsnailDetection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conf_score', models.FloatField()),
                ('frame', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='detection.framedetection')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='detection.species')),
            ],
        ),
    ]
