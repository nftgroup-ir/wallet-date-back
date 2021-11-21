# Generated by Django 3.2.9 on 2021-11-21 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csvmanager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lottery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=120)),
                ('lastname', models.CharField(max_length=120)),
                ('email', models.CharField(max_length=120, unique=True)),
                ('walletaddress', models.CharField(max_length=120, unique=True)),
            ],
        ),
    ]