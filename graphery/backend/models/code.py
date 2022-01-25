from django.db import models

from . import TutorialAnchor, UUIDMixin, TimeDateMixin


__all__ = ["Code"]


class Code(UUIDMixin, TimeDateMixin, models.Model):
    name = models.CharField("code's name", max_length=200, unique=True)
    code = models.TextField("code entity")
    tutorial_anchor = models.OneToOneField(TutorialAnchor, on_delete=models.PROTECT)
