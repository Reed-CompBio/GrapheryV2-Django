# Generated by Django 3.2.14 on 2022-07-29 05:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0025_modify_version_mixin"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="graphdescription",
            name="unique_with_lang_graph_description",
        ),
        migrations.RemoveConstraint(
            model_name="tutorial",
            name="unique_with_lang_tutorial",
        ),
    ]