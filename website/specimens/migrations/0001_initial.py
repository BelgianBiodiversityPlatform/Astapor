# Generated by Django 2.0.1 on 2018-01-11 15:00

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.hstore
import django.contrib.postgres.fields.ranges
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import specimens.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bioregion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
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
            name='Gear',
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
                ('initial_scientific_name', models.CharField(max_length=100)),
                ('uncertain_identification', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('vial', models.CharField(blank=True, max_length=100)),
                ('vial_size', models.CharField(blank=True, max_length=100)),
                ('mnhn_number', models.CharField(blank=True, max_length=100)),
                ('mna_code', models.CharField(blank=True, max_length=100)),
                ('bold_process_id', models.CharField(blank=True, max_length=100)),
                ('bold_sample_id', models.CharField(blank=True, max_length=100)),
                ('bold_bin', models.CharField(blank=True, max_length=100)),
                ('sequence_name', models.CharField(blank=True, max_length=100)),
                ('sequence_fasta', models.TextField(blank=True)),
                ('isotope_d13C', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-40), django.core.validators.MaxValueValidator(-10)], verbose_name=' d13C')),
                ('isotope_d15N', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-5), django.core.validators.MaxValueValidator(30)], verbose_name=' d15N')),
                ('isotope_d34S', models.FloatField(blank=True, null=True, verbose_name=' d34S')),
                ('isotope_percentN', models.FloatField(blank=True, null=True, validators=[specimens.validators.StrictlyMinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name=' %N')),
                ('isotope_percentC', models.FloatField(blank=True, null=True, validators=[specimens.validators.StrictlyMinValueValidator(0), django.core.validators.MaxValueValidator(30)], verbose_name=' %C')),
                ('isotope_percentS', models.FloatField(blank=True, null=True, validators=[specimens.validators.StrictlyMinValueValidator(0)], verbose_name=' %S')),
                ('additional_data', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('bioregion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specimens.Bioregion')),
                ('fixation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specimens.Fixation')),
                ('identified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.Person')),
            ],
            options={
                'ordering': ['specimen_id'],
            },
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
                ('initial_capture_year', models.CharField(blank=True, max_length=5)),
                ('initial_capture_date', models.CharField(blank=True, max_length=100)),
                ('capture_date_start', models.DateField(blank=True, null=True, validators=[specimens.validators.plausible_specimen_date])),
                ('capture_date_end', models.DateField(blank=True, null=True, validators=[specimens.validators.plausible_specimen_date])),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('depth', django.contrib.postgres.fields.ranges.FloatRangeField(blank=True, help_text='Unit: meters.', null=True)),
                ('expedition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.Expedition')),
                ('gear', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specimens.Gear')),
            ],
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('aphia_id', models.IntegerField(blank=True, null=True)),
                ('authority', models.CharField(blank=True, max_length=100)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='specimens.Taxon')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaxonRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TaxonStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='taxon',
            name='rank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specimens.TaxonRank'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specimens.TaxonStatus'),
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
        migrations.AddField(
            model_name='specimen',
            name='taxon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specimens.Taxon'),
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together={('first_name', 'last_name')},
        ),
    ]
