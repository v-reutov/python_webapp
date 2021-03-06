# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-20 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontogen', '0012_auto_20170409_0058'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ont', models.TextField()),
                ('ontology_type', models.CharField(choices=[('subject', 'subject ontology'), ('applied', 'applied ontology')], max_length=50, verbose_name='ontology type')),
            ],
        ),
        migrations.RemoveField(
            model_name='generatorconfig',
            name='instruction',
        ),
        migrations.RemoveField(
            model_name='generatorconfig',
            name='patterns',
        ),
        migrations.RemoveField(
            model_name='historyrecord',
            name='result',
        ),
        migrations.DeleteModel(
            name='GeneratorConfig',
        ),
        migrations.AddField(
            model_name='historyrecord',
            name='results',
            field=models.ManyToManyField(to='ontogen.Ontology'),
        ),
    ]
