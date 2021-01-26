# Generated by Django 3.1.3 on 2020-12-09 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0024_auto_20201209_1638'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controllercomponent',
            name='id',
        ),
        migrations.RemoveField(
            model_name='peripheralcomponent',
            name='id',
        ),
        migrations.AlterField(
            model_name='controllercomponent',
            name='site_entity',
            field=models.OneToOneField(help_text='Which site entity the component is a part of.', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='controller_component', serialize=False, to='farms.siteentity'),
        ),
        migrations.AlterField(
            model_name='peripheralcomponent',
            name='site_entity',
            field=models.OneToOneField(help_text='Which site entity the component is a part of.', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='peripheral_component', serialize=False, to='farms.siteentity'),
        ),
    ]
