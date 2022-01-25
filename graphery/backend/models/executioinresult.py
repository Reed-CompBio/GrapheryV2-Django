from django.db import models

from . import Code, GraphAnchor

__all__ = ["ExecutionResult"]


class ExecutionResult(models.Model):
    code = models.ForeignKey(Code, on_delete=models.PROTECT)
    graph = models.ForeignKey(GraphAnchor, on_delete=models.PROTECT)
    result_json = models.JSONField("execution result json")
    result_json_meta = models.JSONField("execution result json meta data")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code", "graph"],
                name="execution result unique on code and graph",
            )
        ]
