# Generated by Django 3.1.2 on 2020-10-11 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0016_auto_20201009_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controllercomponent',
            name='site_entity',
            field=models.OneToOneField(help_text='Which site entity the component is a part of.', on_delete=django.db.models.deletion.CASCADE, related_name='controller_component', to='farms.siteentity'),
        ),
        migrations.AlterField(
            model_name='controllermessage',
            name='controller',
            field=models.ForeignKey(help_text='The controller associated with the message.', on_delete=django.db.models.deletion.CASCADE, to='farms.controllercomponent'),
        ),
    ]
