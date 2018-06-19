# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-06-18 21:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ontogen', '0016_auto_20180618_1802'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='framesetgranule',
            name='elements',
        ),
        migrations.AddField(
            model_name='granuleitem',
            name='content_type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='granuleitem',
            name='object_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
