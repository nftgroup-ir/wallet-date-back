# Generated by Django 3.2.9 on 2021-12-09 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csvmanager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='hash',
            field=models.CharField(max_length=120, null=True, unique=True),
        ),
    ]