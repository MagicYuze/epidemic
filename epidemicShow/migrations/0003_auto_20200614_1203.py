# Generated by Django 3.0.7 on 2020-06-14 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epidemicShow', '0002_auto_20200614_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epidemicinfo',
            name='time',
            field=models.DateField(blank=True, null=True),
        ),
    ]
