from django.db import models

from . import (
    UUIDMixin,
    TimeDateMixin,
    StatusMixin,
    LangMixin,
    Tag,
    User,
    unique_with_lang,
)


class TutorialAnchor(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    url = models.CharField("tutorial url", max_length=150, unique=True)
    anchor_name = models.CharField("tutorial anchor name", max_length=200, unique=True)
    tags = models.ManyToManyField(Tag)


class Tutorial(UUIDMixin, TimeDateMixin, StatusMixin, LangMixin, models.Model):
    tutorial_anchor = models.ForeignKey(TutorialAnchor, on_delete=models.PROTECT)
    authors = models.ManyToManyField(User)
    title = models.CharField("tutorial title", max_length=300, null=False, blank=False)
    abstract = models.TextField("tutorial abstract", null=False)
    content_markdown = models.TextField("tutorial content in Markdown", null=False)

    @unique_with_lang("tutorial_anchor", "tutorial")
    class Meta:
        pass
