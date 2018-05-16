# Generated by Django 2.0.4 on 2018-05-14 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0004_auto_20180513_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifier',
            name='notify_status',
            field=models.CharField(choices=[('Draft', 'Draft'), ('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Incomplete', 'Incomplete'), ('Failed', 'Failed')], default='Draft', max_length=10),
        ),
    ]
