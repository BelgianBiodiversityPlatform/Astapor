# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-21 07:43
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Expedition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Fixation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'people',
            },
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specimen_id', models.IntegerField(unique=True)),
                ('scientific_name', models.CharField(max_length=100)),
                ('coords', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Coordinates')),
                ('depth', django.contrib.postgres.fields.ranges.FloatRangeField(blank=True, help_text='Unit: meters.', null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('fixation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specimens.Fixation')),
                ('identified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.Person')),
            ],
        ),
        migrations.CreateModel(
            name='SpecimenLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SpecimenPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='specimen_pictures')),
                ('high_interest', models.BooleanField(verbose_name='High resolution/species representative')),
                ('specimen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.Specimen')),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('expedition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.Expedition')),
            ],
        ),
        migrations.AddField(
            model_name='specimen',
            name='specimen_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.SpecimenLocation'),
        ),
        migrations.AddField(
            model_name='specimen',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.Station'),
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together=set([('first_name', 'last_name')]),
        ),
    ]
