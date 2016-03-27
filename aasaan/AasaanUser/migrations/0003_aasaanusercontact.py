# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-27 09:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contacts', '0016_auto_20160225_2129'),
        ('AasaanUser', '0002_auto_20160110_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='AasaanUserContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
