# Generated by Django 3.2.13 on 2022-06-08 19:00

from django.db import migrations, models


def provide_default_rank(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    model = apps.get_model("backend", "TutorialAnchor")  # type: TutorialAnchor
    rank_num = 0
    for obj in model.objects.using(db_alias).all():
        rank_num += 1
        obj.rank = f"{rank_num:03}"
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0020_fix_execution_result_mixin"),
    ]

    operations = [
        migrations.AddField(
            model_name="tutorialanchor",
            name="rank",
            field=models.CharField(default="001", max_length=3, unique=False),
            preserve_default=False,
        ),
        migrations.RunPython(provide_default_rank, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="tutorialanchor",
            name="rank",
            field=models.CharField(max_length=3, unique=True),
        ),
    ]
