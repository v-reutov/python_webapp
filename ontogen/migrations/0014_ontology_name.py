# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-20 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontogen', '0013_auto_20170420_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='ontology',
            name='name',
            field=models.CharField(default='asd', max_length=50, verbose_name='ontology name'),
            preserve_default=False,
        ),
    ]
