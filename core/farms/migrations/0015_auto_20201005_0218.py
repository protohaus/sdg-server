# Generated by Django 3.1.2 on 2020-10-05 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0014_add_hypertables'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controllermessage',
            name='message',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='mqttmessage',
            name='message',
            field=models.JSONField(),
        ),
    ]
