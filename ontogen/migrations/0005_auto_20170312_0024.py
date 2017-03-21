# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-11 19:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ontogen', '0004_auto_20170312_0015'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mapping_label', models.CharField(max_length=50)),
                ('mapping_value', models.CharField(max_length=100)),
            ],
        ),
        migrations.RenameField(
            model_name='pattern',
            old_name='pattern',
            new_name='pattern_text',
        ),
        migrations.RemoveField(
            model_name='pattern',
            name='mapping',
        ),
        migrations.AddField(
            model_name='mapping',
            name='pattern',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ontogen.Pattern'),
        ),
    ]