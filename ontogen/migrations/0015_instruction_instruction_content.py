# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-05-27 12:50
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontogen', '0014_ontology_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='instruction_content',
            field=ckeditor.fields.RichTextField(default='', verbose_name='instruction content'),
        ),
    ]