# Generated by Django 2.0.4 on 2018-09-24 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travels', '0011_travelrequest_ticket_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travelrequest',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='travelrequest',
            name='refund_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
