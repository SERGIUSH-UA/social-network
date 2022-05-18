# Generated by Django 4.0.4 on 2022-05-17 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='native_city',
            field=models.CharField(default='', max_length=80, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='user',
            name='native_country',
            field=models.CharField(default='', max_length=80, verbose_name='Country'),
        ),
    ]