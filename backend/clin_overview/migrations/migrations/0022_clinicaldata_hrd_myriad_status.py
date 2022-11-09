# Generated by Django 3.2.16 on 2022-11-03 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clin_overview', '0021_clinicaldata_hr_signature_per_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicaldata',
            name='hrd_myriad_status',
            field=models.CharField(choices=[('HRDPOSITIVE', 'HRD positive'), ('HRDNEGATIVE', 'HRD negative')], max_length=100, null=True),
        ),
    ]
