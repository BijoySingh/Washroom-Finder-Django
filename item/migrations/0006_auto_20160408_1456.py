# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-08 09:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0005_item_is_free'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
