from django.db import models

from . import (
    UUIDMixin,
    TimeDateMixin,
    StatusMixin,
    LangMixin,
    TagAnchor,
    User,
    unique_with_lang,
    GraphOrder,
    TutorialAnchor,
)


__all__ = ["GraphAnchor", "Graph", "OrderedGraphAnchor", "GraphDescription"]


class GraphAnchor(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    url = models.SlugField("graph url", max_length=150, unique=True)
    anchor_name = models.CharField("graph anchor name", max_length=200, unique=True)
    tag_anchors = models.ManyToManyField(TagAnchor, related_name="graph_anchors")
    default_order = models.PositiveIntegerField(
        "graph default order", choices=GraphOrder.choices, default=GraphOrder.LOW
    )
    tutorial_anchors = models.ManyToManyField(
        TutorialAnchor, through="OrderedGraphAnchor", related_name="graph_anchors"
    )


class OrderedGraphAnchor(UUIDMixin, TimeDateMixin, models.Model):
    graph_anchor = models.ForeignKey(GraphAnchor, on_delete=models.CASCADE)
    tutorial_anchor = models.ForeignKey(TutorialAnchor, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        "graph order", choices=GraphOrder.choices, default=GraphOrder.LOW
    )


class Graph(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    graph_anchor = models.OneToOneField(
        GraphAnchor, on_delete=models.PROTECT, related_name="graph"
    )
    graph_json = models.JSONField("graph json")
    makers = models.ManyToManyField(User, related_name="graphs")


class GraphDescription(UUIDMixin, TimeDateMixin, StatusMixin, LangMixin, models.Model):
    graph_anchor = models.ForeignKey(
        GraphAnchor, on_delete=models.PROTECT, related_name="graph_descriptions"
    )
    authors = models.ManyToManyField(User, related_name="graph_descriptions")
    title = models.CharField("graph description title", max_length=300)
    description_markdown = models.TextField("graph description markdown")

    @unique_with_lang("graph_anchor", "graph_description")
    class Meta:
        pass
