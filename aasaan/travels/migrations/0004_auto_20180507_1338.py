# Generated by Django 2.0.4 on 2018-05-07 08:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0003_auto_20180507_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travelrequest',
            name='onward_date',
            field=models.DateTimeField(default=datetime.date.today, verbose_name='Date of Journey'),
        ),
    ]
