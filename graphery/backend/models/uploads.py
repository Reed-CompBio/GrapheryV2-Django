from django.db import models

from . import UUIDMixin, TimeDateMixin, TutorialAnchor, GraphAnchor

__all__ = ["Uploads"]


class Uploads(UUIDMixin, TimeDateMixin, models.Model):
    file = models.FileField()
    name = models.CharField("file name", max_length=300)

    tutorial_anchors = models.ManyToManyField(TutorialAnchor, related_name="uploads")
    graph_anchors = models.ManyToManyField(GraphAnchor, related_name="uploads")
