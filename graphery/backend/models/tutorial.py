from django.db import models

from . import (
    UUIDMixin,
    TimeDateMixin,
    StatusMixin,
    LangMixin,
    TagAnchor,
    User,
    unique_with_lang,
)

__all__ = ["TutorialAnchor", "Tutorial"]


class TutorialAnchor(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    url = models.CharField("tutorial url", max_length=150, unique=True)
    anchor_name = models.CharField("tutorial anchor name", max_length=200, unique=True)
    tag_anchors = models.ManyToManyField(TagAnchor, related_name="tutorial_anchors")


class Tutorial(UUIDMixin, TimeDateMixin, StatusMixin, LangMixin, models.Model):
    tutorial_anchor = models.ForeignKey(
        TutorialAnchor, on_delete=models.PROTECT, related_name="tutorials"
    )
    authors = models.ManyToManyField(User, related_name="tutorials")
    title = models.CharField("tutorial title", max_length=300, null=False, blank=False)
    abstract = models.TextField("tutorial abstract", null=False)
    content_markdown = models.TextField("tutorial content in Markdown", null=False)

    @unique_with_lang("tutorial_anchor", "tutorial")
    class Meta:
        pass
