# Generated by Django 3.1 on 2020-09-20 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200919_1128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coeficientevalor',
            name='coeficiente',
        ),
        migrations.RemoveField(
            model_name='grupocoeficientes',
            name='casa',
        ),
        migrations.RemoveField(
            model_name='consumomes',
            name='reduzir_agua_feriado',
        ),
        migrations.RemoveField(
            model_name='consumomes',
            name='reduzir_agua_semana',
        ),
        migrations.RemoveField(
            model_name='consumomes',
            name='reduzir_energia_feriado',
        ),
        migrations.RemoveField(
            model_name='consumomes',
            name='reduzir_energia_semana',
        ),
        migrations.DeleteModel(
            name='Coeficiente',
        ),
        migrations.DeleteModel(
            name='CoeficienteValor',
        ),
        migrations.DeleteModel(
            name='GrupoCoeficientes',
        ),
    ]
