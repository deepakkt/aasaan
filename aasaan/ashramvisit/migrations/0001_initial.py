# Generated by Django 2.0.4 on 2018-05-01 07:13

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AshramVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_date', models.DateTimeField(verbose_name='Arrival Date & Time')),
                ('departure_time', models.TimeField(verbose_name='Departure Time')),
                ('participant_count', models.IntegerField()),
                ('lunch', models.BooleanField()),
                ('dinner', models.BooleanField()),
                ('contact_person', models.CharField(max_length=100)),
                ('mobile_no', models.CharField(max_length=15, verbose_name='Mobile Number')),
                ('Center', smart_selects.db_fields.GroupedForeignKey(group_field='zone', on_delete=django.db.models.deletion.CASCADE, to='contacts.Center')),
            ],
        ),
    ]
