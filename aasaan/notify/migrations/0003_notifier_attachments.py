# Generated by Django 2.0.4 on 2018-05-12 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0002_remove_notifier_centers'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifier',
            name='attachments',
            field=models.TextField(blank=True),
        ),
    ]
