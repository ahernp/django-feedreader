# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=2000, null=True, blank=True)),
                ('link', models.CharField(max_length=2000)),
                ('description', models.TextField(null=True, blank=True)),
                ('published_time', models.DateTimeField(auto_now_add=True)),
                ('read_flag', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-published_time'],
                'verbose_name_plural': 'entries',
            },
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=2000, null=True, blank=True)),
                ('xml_url', models.CharField(unique=True, max_length=255)),
                ('link', models.CharField(max_length=2000, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('published_time', models.DateTimeField(null=True, blank=True)),
                ('last_polled_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number_initially_displayed', models.IntegerField(default=10)),
                ('number_additionally_displayed', models.IntegerField(default=5)),
                ('max_entries_saved', models.IntegerField(default=100)),
            ],
            options={
                'verbose_name_plural': 'options',
            },
        ),
        migrations.AddField(
            model_name='feed',
            name='group',
            field=models.ForeignKey(blank=True, to='feedreader.Group', null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='feed',
            field=models.ForeignKey(to='feedreader.Feed'),
        ),
    ]
