# Generated by Django 3.2.16 on 2022-11-03 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clin_overview', '0014_auto_20221103_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicaldata',
            name='progression',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]