# Generated by Django 3.2.12 on 2022-03-24 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0012_auto_20220321_0555"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="graphanchor",
            name="tags",
        ),
        migrations.AddField(
            model_name="graphanchor",
            name="tag_anchors",
            field=models.ManyToManyField(
                related_name="graph_anchors", to="backend.TagAnchor"
            ),
        ),
    ]
