# Generated by Django 2.0.4 on 2018-09-08 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0010_auto_20180614_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelrequest',
            name='ticket_number',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
