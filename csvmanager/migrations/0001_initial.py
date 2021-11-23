# Generated by Django 3.2.9 on 2021-11-23 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CSV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=120, unique=True)),
                ('email', models.CharField(blank=True, max_length=120)),
                ('points', models.CharField(blank=True, max_length=120)),
                ('transactions', models.IntegerField(null=True)),
                ('balance', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
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
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactions', models.JSONField()),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvmanager.csv')),
            ],
        ),
        migrations.CreateModel(
            name='NFT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nfts', models.JSONField()),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvmanager.csv')),
            ],
        ),
        migrations.CreateModel(
            name='BalanceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.JSONField()),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvmanager.csv')),
            ],
        ),
    ]
