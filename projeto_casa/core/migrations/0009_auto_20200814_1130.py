# Generated by Django 3.0.8 on 2020-08-14 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200811_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comodosaida',
            name='tempo_max_feriado',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='comodosaida',
            name='tempo_max_semana',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='comodosaida',
            name='tempo_min_feriado',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='comodosaida',
            name='tempo_min_semana',
            field=models.IntegerField(null=True),
        ),
    ]
