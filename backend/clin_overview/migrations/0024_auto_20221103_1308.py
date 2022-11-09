# Generated by Django 3.2.16 on 2022-11-03 12:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clin_overview', '0023_auto_20221103_1300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clinicaldata',
            name='cancer_in_family',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='current_treatment_phase',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='disease_origin',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='extra_patient_info',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='has_ctdna',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='has_germline_control',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='has_paired_freshsample',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='has_petct',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='has_response_ct',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='has_singlecell',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='maintenance_therapy',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='other_diagnosis',
        ),
        migrations.RemoveField(
            model_name='clinicaldata',
            name='other_medication',
        ),
    ]
