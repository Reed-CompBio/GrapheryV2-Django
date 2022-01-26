from django.db import models

from . import (
    UUIDMixin,
    TimeDateMixin,
    StatusMixin,
    LangMixin,
    Tag,
    User,
    unique_with_lang,
    GraphOrder,
    TutorialAnchor,
)


__all__ = ["GraphAnchor", "Graph", "GraphDescription"]


class GraphAnchor(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    url = models.CharField("graph url", max_length=150, unique=True)
    anchor_name = models.CharField("graph anchor name", max_length=200, unique=True)
    tags = models.ManyToManyField(Tag)
    default_order = models.PositiveIntegerField(
        "graph default order", choices=GraphOrder.choices, default=GraphOrder.LOW
    )
    tutorial_anchor = models.ManyToManyField(
        TutorialAnchor, through="OrderedGraphAnchor"
    )


class OrderedGraphAnchor(models.Model):
    graph_anchor = models.ForeignKey(GraphAnchor, on_delete=models.CASCADE)
    tutorial_anchor = models.ForeignKey(TutorialAnchor, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        "graph order", choices=GraphOrder.choices, default=GraphOrder.LOW
    )


class Graph(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    graph_anchor = models.OneToOneField(GraphAnchor, on_delete=models.PROTECT)
    graph_json = models.JSONField("graph json")
    makers = models.ManyToManyField(User)


class GraphDescription(UUIDMixin, TimeDateMixin, StatusMixin, LangMixin, models.Model):
    graph_anchor = models.ForeignKey(GraphAnchor, on_delete=models.PROTECT)
    authors = models.ManyToManyField(User)
    title = models.CharField("graph description title", max_length=300)
    description_markdown = models.TextField("graph description markdown")

    @unique_with_lang("graph_anchor", "graph_description")
    class Meta:
        pass
