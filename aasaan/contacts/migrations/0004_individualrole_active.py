# Generated by Django 2.0.4 on 2018-09-11 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_remove_contact_id_proof_other'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualrole',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
