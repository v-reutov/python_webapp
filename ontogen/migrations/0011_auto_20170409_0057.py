# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-08 19:57
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ontogen', '0010_pattern_extracted_elements_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=datetime.datetime(2017, 4, 8, 19, 57, 26, 192145, tzinfo=utc))),
                ('result', models.TextField()),
            ],
            options={
                'ordering': ('datetime', 'user'),
            },
        ),
        migrations.AlterField(
            model_name='instruction',
            name='instruction_label',
            field=models.CharField(max_length=50, verbose_name='instruction label'),
        ),
        migrations.AlterField(
            model_name='instruction',
            name='instruction_text',
            field=models.TextField(verbose_name='instruction text'),
        ),
        migrations.AlterField(
            model_name='mapping',
            name='mapping_label',
            field=models.CharField(max_length=50, verbose_name='mapping label'),
        ),
        migrations.AlterField(
            model_name='mapping',
            name='mapping_value',
            field=models.CharField(max_length=100, verbose_name='mapping value'),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='extracted_elements_type',
            field=models.CharField(choices=[(None, '-'), ('concept', 'Concept'), ('relation', 'Relation')], default='concept', max_length=50, verbose_name='extracted elements type'),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='pattern_label',
            field=models.CharField(max_length=50, verbose_name='pattern label'),
        ),
        migrations.AlterField(
            model_name='pattern',
            name='pattern_text',
            field=models.CharField(max_length=200, verbose_name='pattern text'),
        ),
        migrations.AddField(
            model_name='historyrecord',
            name='instruction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ontogen.Instruction'),
        ),
        migrations.AddField(
            model_name='historyrecord',
            name='patterns',
            field=models.ManyToManyField(to='ontogen.Pattern'),
        ),
        migrations.AddField(
            model_name='historyrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
