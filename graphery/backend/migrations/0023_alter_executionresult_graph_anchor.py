# Generated by Django 3.2.14 on 2022-07-07 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0022_auto_20220707_1730"),
    ]

    operations = [
        migrations.AlterField(
            model_name="executionresult",
            name="graph_anchor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="execution_results",
                to="backend.graphanchor",
            ),
        ),
    ]
