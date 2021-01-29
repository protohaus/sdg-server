# Generated by Django 3.0.9 on 2020-08-30 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0009_controllertoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controller',
            name='user',
        ),
        migrations.AddField(
            model_name='controller',
            name='site',
            field=models.ForeignKey(help_text='The site to which the controller is assigned to.', null=True, on_delete=django.db.models.deletion.CASCADE, to='farms.Site'),
        ),
    ]