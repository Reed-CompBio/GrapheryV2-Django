from __future__ import annotations

from django.db import models

from ..data_bridge import (
    DataBridgeBase,
    DataBridgeProtocol,
)
from ..models import UUIDMixin, LangMixin, StatusMixin


def test_data_bridge_meta():
    class TestModel(models.Model):
        test_field = models.CharField(max_length=100)

    # noinspection PyUnusedLocal
    class AuxModel(models.Model):
        test_model = models.ForeignKey(
            TestModel, on_delete=models.CASCADE, related_name="reverse_fk_name"
        )
        test_models = models.ManyToManyField(TestModel, related_name="reverse_m2m_name")
        test_single_model = models.OneToOneField(
            TestModel, on_delete=models.CASCADE, related_name="reverse_o2o_name"
        )

    class BridgeTestModel(DataBridgeProtocol):
        _bridged_model = TestModel

        def _bridges_test_field(self):
            pass

        def _bridges_reverse_fk_name(self):
            pass

        def _bridges_reverse_m2m_name(self):
            pass

        def _bridges_reverse_o2o_name(self):
            pass

    assert len(BridgeTestModel._bridges) == 4
    fns = list(BridgeTestModel._bridges.values())

    assert BridgeTestModel._bridges_test_field in fns
    assert BridgeTestModel._bridges_reverse_fk_name in fns
    assert BridgeTestModel._bridges_reverse_m2m_name in fns
    assert BridgeTestModel._bridges_reverse_o2o_name in fns


def test_data_bridge_base():
    class TestModel(models.Model):
        pass

    class BridgeTest(DataBridgeBase):
        _bridged_model = TestModel

    assert len(BridgeTest._bridges) == 0


def test_data_bridge_mixin():
    class TestModel(UUIDMixin, LangMixin, StatusMixin, models.Model):
        pass

    class BridgeTest(DataBridgeProtocol):
        _bridged_model = TestModel

    assert len(BridgeTest._bridges) == 3
