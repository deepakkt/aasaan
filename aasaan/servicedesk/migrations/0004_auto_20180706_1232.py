# Generated by Django 2.0.4 on 2018-07-06 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicedesk', '0003_auto_20180627_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
