# Generated by Django 3.0.8 on 2020-08-15 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20200814_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comodosaida',
            name='essencial',
            field=models.BooleanField(default=False),
        ),
    ]
