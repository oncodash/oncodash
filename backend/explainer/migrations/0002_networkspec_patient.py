# Generated by Django 3.2.10 on 2022-01-04 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explainer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkspec',
            name='patient',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]