# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-14 13:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specimen_id', models.IntegerField(unique=True)),
                ('scientific_name', models.CharField(max_length=100)),
                ('depth', models.IntegerField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
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
        migrations.AddField(
            model_name='specimen',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.SpecimenLocation'),
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together=set([('first_name', 'last_name')]),
        ),
    ]
