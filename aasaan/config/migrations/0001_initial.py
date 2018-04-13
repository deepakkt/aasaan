# Generated by Django 2.0.4 on 2018-04-13 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('configuration_key', models.CharField(max_length=100, unique=True)),
                ('configuration_value', models.TextField()),
                ('configuration_description', models.TextField(blank=True, verbose_name='a brief description of this setting')),
            ],
            options={
                'ordering': ['configuration_key'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ['tag_name'],
            },
        ),
    ]
