# Generated by Django 3.0.8 on 2020-08-04 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200802_2231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipoequipamento',
            name='essencial',
        ),
        migrations.AddField(
            model_name='comodosaida',
            name='essencial',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
