# Generated by Django 3.2.16 on 2022-11-03 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clin_overview', '0025_alter_clinicaldata_patient_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicaldata',
            name='patient_id',
            field=models.IntegerField(unique=True),
        ),
    ]