# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Center',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('center_name', models.CharField(max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('first_name', models.CharField(verbose_name='first Name', max_length=50)),
                ('last_name', models.CharField(verbose_name='last Name', max_length=50)),
                ('teacher_tno', models.CharField(verbose_name='teacher number', max_length=7, blank=True)),
                ('date_of_birth', models.DateField(null=True, verbose_name='date of birth', blank=True)),
                ('gender', models.CharField(max_length=2, choices=[('M', 'Male'), ('F', 'Female'), ('TG', 'Transgender')])),
                ('status', models.CharField(max_length=6, choices=[('STAFF', 'Staff'), ('INACTV', 'Inactive'), ('EXPD', 'Deceased'), ('FT', 'Full Time'), ('PT', 'Part Time'), ('VOL', 'Volunteer')], blank=True)),
                ('cug_mobile', models.CharField(verbose_name='cUG phone number', max_length=15, blank=True)),
                ('other_mobile_1', models.CharField(verbose_name='alternate mobile 1', max_length=15, blank=True)),
                ('other_mobile_2', models.CharField(verbose_name='alternate mobile 2', max_length=15, blank=True)),
                ('whatsapp_number', models.CharField(verbose_name='whatsapp number', max_length=15, blank=True)),
                ('primary_email', models.EmailField(verbose_name='primary Email', max_length=50)),
                ('secondary_email', models.EmailField(verbose_name='secondary Email', max_length=50, blank=True)),
                ('pushbullet_token', models.CharField(verbose_name='pushbullet Token', max_length=64, blank=True)),
                ('id_card_type', models.CharField(verbose_name='iD Card Type', max_length=10, blank=True)),
                ('id_card_number', models.CharField(verbose_name='iD Card Number', max_length=20, blank=True)),
                ('id_proof_type', models.CharField(verbose_name='iD Proof Type', max_length=2, choices=[('DL', 'Driving License'), ('PP', 'Passport'), ('RC', 'Ration Card'), ('VC', 'Voters ID'), ('AA', 'Aadhaar'), ('PC', 'PAN Card'), ('OT', 'Other Government Issued')], blank=True)),
                ('id_proof_number', models.CharField(verbose_name='iD Card Number', max_length=30, blank=True)),
                ('id_proof_other', models.CharField(verbose_name='type of ID if other', max_length=30, blank=True)),
                ('profile_picture', models.ImageField(upload_to='profile_pictures', blank=True)),
                ('remarks', models.TextField(max_length=500, blank=True)),
            ],
            options={
                'verbose_name': 'PCC Contact',
                'ordering': ['first_name', 'last_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('address_type', models.CharField(verbose_name='address Type', max_length=2, choices=[('WO', 'Work'), ('HO', 'Home')])),
                ('address_line_1', models.CharField(max_length=100)),
                ('address_line_2', models.CharField(max_length=100)),
                ('address_line_3', models.CharField(max_length=100, blank=True)),
                ('city', models.CharField(max_length=50)),
                ('postal_code', models.CharField(max_length=10)),
                ('state', models.CharField(max_length=25, blank=True)),
                ('country', models.CharField(max_length=25, blank=True)),
                ('contact_number', models.CharField(verbose_name='contact number for this address', max_length=15, blank=True)),
                ('contact', models.ForeignKey(to='contacts.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('note_type', models.CharField(max_length=2, choices=[('SC', 'Status Change'), ('CN', 'Critical Note'), ('MN', 'Medical Note'), ('IN', 'Information Note')])),
                ('note', models.TextField(max_length=500)),
                ('note_timestamp', models.DateTimeField(auto_now_add=True)),
                ('contact', models.ForeignKey(to='contacts.Contact')),
            ],
            options={
                'ordering': ['-note_timestamp'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('contact', models.ForeignKey(to='contacts.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('contact', models.ForeignKey(to='contacts.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('role_name', models.CharField(max_length=50)),
                ('role_remarks', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'PCC Role',
                'ordering': ['role_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sector_name', models.CharField(max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('zone_name', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'PCC Zone',
                'ordering': ['zone_name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sector',
            name='zone',
            field=models.ForeignKey(to='contacts.Zone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contactzone',
            name='zone',
            field=models.ForeignKey(to='contacts.Zone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contactrole',
            name='role',
            field=models.ForeignKey(to='contacts.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='center',
            name='sector',
            field=models.ForeignKey(to='contacts.Sector'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='center',
            name='zone',
            field=models.ForeignKey(to='contacts.Zone'),
            preserve_default=True,
        ),
    ]
