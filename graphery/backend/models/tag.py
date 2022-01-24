from django.db import models

from . import UUIDMixin, TimeDateMixin, StatusMixin, LangMixin, unique_with_lang


__all__ = ["TagAnchor", "Tag"]


class TagAnchor(UUIDMixin, TimeDateMixin, StatusMixin, models.Model):
    anchor_name = models.CharField(
        "tag anchor name", max_length=150, null=False, blank=False, unique=True
    )


class Tag(UUIDMixin, TimeDateMixin, StatusMixin, LangMixin, models.Model):
    name = models.CharField(
        "tag displayed name", max_length=150, null=False, blank=False, unique=True
    )
    tag_anchor = models.ForeignKey(TagAnchor, on_delete=models.CASCADE)
    description = models.CharField(
        "tag description", max_length=512, null=False, blank=True
    )

    @unique_with_lang("tag_anchor", "tag")
    class Meta:
        pass
