# Generated by Django 3.0.8 on 2020-08-23 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200822_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumohora',
            name='data',
            field=models.DateField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='consumohora',
            name='hora',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
