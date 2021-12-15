# Generated by Django 3.2.9 on 2021-12-14 13:38

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
                ('address', models.CharField(max_length=120, unique=True)),
                ('total_nfts', models.BigIntegerField(null=True)),
                ('total_Txs', models.BigIntegerField(null=True)),
                ('balance', models.TextField(null=True)),
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
                ('hash', models.CharField(max_length=120, null=True, unique=True)),
                ('nonc', models.IntegerField(null=True)),
                ('transaction_index', models.IntegerField(null=True)),
                ('from_address', models.CharField(max_length=120, null=True)),
                ('to_address', models.CharField(max_length=120, null=True)),
                ('value', models.CharField(max_length=120, null=True)),
                ('gas', models.IntegerField(null=True)),
                ('gas_price', models.BigIntegerField(null=True)),
                ('input', models.CharField(max_length=120, null=True)),
                ('receipt_cumulative_gas_used', models.IntegerField(null=True)),
                ('receipt_gas_used', models.IntegerField(null=True)),
                ('receipt_contract_address', models.CharField(max_length=120, null=True)),
                ('receipt_root', models.CharField(max_length=120, null=True)),
                ('receipt_status', models.IntegerField(null=True)),
                ('block_timestamp', models.DateTimeField(null=True)),
                ('block_number', models.IntegerField(null=True)),
                ('block_hash', models.CharField(max_length=120, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvmanager.csv')),
            ],
        ),
        migrations.CreateModel(
            name='NFT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_address', models.TextField(null=True)),
                ('token_id', models.TextField(null=True)),
                ('block_number_minted', models.TextField(null=True)),
                ('owner_of', models.TextField(null=True)),
                ('block_number', models.TextField(null=True)),
                ('amount', models.IntegerField(null=True)),
                ('contract_type', models.TextField(null=True)),
                ('name', models.TextField(null=True)),
                ('symbol', models.TextField(null=True)),
                ('token_uri', models.TextField(null=True)),
                ('metadata', models.TextField(null=True)),
                ('synced_at', models.DateTimeField(null=True)),
                ('is_valid', models.IntegerField(null=True)),
                ('syncing', models.TextField(null=True)),
                ('frozen', models.TextField(null=True)),
                ('field_unique', models.TextField(null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvmanager.csv')),
            ],
        ),
        migrations.CreateModel(
            name='BalanceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_decimals', models.BigIntegerField(null=True)),
                ('contract_name', models.TextField(null=True)),
                ('contract_ticker_symbol', models.TextField(null=True)),
                ('contract_address', models.CharField(max_length=120, null=True, unique=True)),
                ('logo_url', models.TextField(null=True)),
                ('last_transferred_at', models.DateTimeField(null=True)),
                ('type', models.TextField(null=True)),
                ('balance', models.TextField(null=True)),
                ('balance_24h', models.TextField(null=True)),
                ('quote_rate', models.TextField(null=True)),
                ('quote_rate_24h', models.TextField(null=True)),
                ('quote', models.TextField(null=True)),
                ('quote_24h', models.TextField(null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csvmanager.csv')),
            ],
        ),
    ]
