# Generated by Django 3.0.8 on 2020-08-26 02:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20200825_2244'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumohora',
            name='status',
        ),
        migrations.AddField(
            model_name='comodosaida',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelTable(
            name='coeficientevalor',
            table='coeficiente_valor',
        ),
        migrations.CreateModel(
            name='GrupoCoeficientes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precisao', models.DecimalField(decimal_places=1, default=0, max_digits=4)),
                ('status', models.BooleanField(default=False)),
                ('casa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Casa')),
            ],
            options={
                'db_table': 'grupo_coeficientes',
            },
        ),
        migrations.AddField(
            model_name='coeficiente',
            name='grupo',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.GrupoCoeficientes'),
            preserve_default=False,
        ),
    ]
