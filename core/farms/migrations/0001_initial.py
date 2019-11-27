# Generated by Django 2.2.7 on 2019-11-26 11:40

import address.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import macaddress.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('address', '0002_auto_20160213_1726'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The UUID to identify the hydroponic system.', primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='The name of the farm.', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the farm was first created.')),
                ('modified_at', models.DateTimeField(auto_now=True, help_text='The date and time when the farm was last updated.')),
                ('address', address.models.AddressField(help_text='The postal address and the coordinates of the farm', null=True, on_delete=django.db.models.deletion.SET_NULL, to='address.Address')),
                ('owner', models.ForeignKey(help_text='The user that owns the farm.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HydroponicSystem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The UUID to identify the hydroponic system.', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, help_text='The name of the hydroponic system', max_length=30, null=True)),
                ('system_type', models.CharField(choices=[('VT', 'Vertical tower'), ('FD', 'Flood and drain'), ('NFT', 'Nutrient film technique'), ('DWC', 'Deep water culture')], default='VT', help_text="The hydroponic system's type (e.g., vertical tower, flood and drain).", max_length=3)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the hydroponic system was first registered.')),
                ('modified_at', models.DateTimeField(auto_now=True, help_text='The date and time when the hydroponic system was last updated.')),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farms.Farm')),
            ],
        ),
        migrations.CreateModel(
            name='Coordinator',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The UUID to identify the hydroponic system.', primary_key=True, serialize=False)),
                ('local_ip_address', models.GenericIPAddressField(help_text="The coordinator's local IP address.")),
                ('external_ip_address', models.GenericIPAddressField(help_text="The coordinator's external IP address.")),
                ('dns_address', models.URLField(blank=True, help_text='The URL which can be used to find the local IP address.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the coordinator was first registered.')),
                ('modified_at', models.DateTimeField(auto_now=True, help_text='The date and time when the coordinator was last updated.')),
                ('farm', models.OneToOneField(blank=True, help_text='The farm to which the coordinator belongs.', null=True, on_delete=django.db.models.deletion.CASCADE, to='farms.Farm')),
            ],
        ),
        migrations.CreateModel(
            name='Controller',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The UUID to identify the controller.', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, help_text='The name of the controller', max_length=30, null=True)),
                ('wifi_mac_address', macaddress.fields.MACAddressField(help_text='The Wifi MAC address of the controller.', integer=True)),
                ('external_ip_address', models.GenericIPAddressField(blank=True, help_text='The external IP address of the controller.', null=True)),
                ('controller_type', models.CharField(choices=[('PC', 'Pump controller'), ('DC', 'Dosage controller'), ('CC', 'Camera controller'), ('SC', 'Sensor controller')], default='PC', help_text='The main function of the controller (e.g., pump or sensor controller).', max_length=3)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the controller was first registered.')),
                ('modified_at', models.DateTimeField(auto_now=True, help_text='The date and time when the controller was last updated.')),
                ('farm', models.ForeignKey(blank=True, help_text='The farm to which the controller belongs to, and thus the coordinator.', null=True, on_delete=django.db.models.deletion.CASCADE, to='farms.Farm')),
            ],
        ),
    ]
