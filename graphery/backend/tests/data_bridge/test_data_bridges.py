from __future__ import annotations

import pytest
from django.db import models
from strawberry import UNSET

from ..utils import make_request_with_user
from ...data_bridge import DataBridgeBase, DataBridgeProtocol, ValidationError
from ...models import UUIDMixin, LangMixin, StatusMixin, Status


def test_data_bridge_meta():
    class BaseModel(models.Model):
        pass

    class TestModel(models.Model):
        test_field = models.CharField(max_length=100)
        test_forward_fk = models.ForeignKey(
            BaseModel, on_delete=models.CASCADE, related_name="test_backward_fk"
        )
        test_forward_m2m = models.ManyToManyField(
            BaseModel, related_name="test_backward_m2m"
        )
        test_forward_o2o = models.OneToOneField(
            BaseModel, on_delete=models.CASCADE, related_name="test_backward_o2o"
        )

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
        _bridged_model_cls = TestModel

        def _bridges_test_field(self):
            pass

        def _bridges_test_forward_fk(self):
            pass

        def _bridges_test_forward_m2m(self):
            pass

        def _bridges_test_forward_o2o(self):
            pass

        def _bridges_reverse_fk_name(self):
            pass

        def _bridges_reverse_m2m_name(self):
            pass

        def _bridges_reverse_o2o_name(self):
            pass

    assert len(BridgeTestModel._bridges) == 7
    fns = list(fn.__wrapped__ for fn in BridgeTestModel._bridges.values())

    assert BridgeTestModel._bridges_test_field in fns
    assert BridgeTestModel._bridges_test_forward_fk in fns
    assert BridgeTestModel._bridges_test_forward_m2m in fns
    assert BridgeTestModel._bridges_test_forward_o2o in fns
    assert BridgeTestModel._bridges_reverse_fk_name in fns
    assert BridgeTestModel._bridges_reverse_m2m_name in fns
    assert BridgeTestModel._bridges_reverse_o2o_name in fns


def test_data_bridge_base():
    class TestModel(models.Model):
        pass

    class BridgeTest(DataBridgeBase):
        __slots__ = ()
        _bridged_model_cls = TestModel

    assert len(BridgeTest._bridges) == 0


def test_data_bridge_mixin():
    class TestModel(UUIDMixin, LangMixin, StatusMixin, models.Model):
        pass

    class BridgeTest(DataBridgeProtocol):
        _bridged_model_cls = TestModel

    assert len(BridgeTest._bridges) == 3


def test_data_bridge_status_mixin(rf, admin_user, editor_user, translator_user):
    class TestModel(UUIDMixin, StatusMixin, models.Model):
        pass

    class BridgeTest(DataBridgeBase):
        _bridged_model_cls = TestModel

    admin_request = make_request_with_user(rf, admin_user)
    BridgeTest(UNSET).get_instance()._bridges_item_status(
        Status.PUBLISHED, request=admin_request
    )

    editor_request = make_request_with_user(rf, editor_user)
    BridgeTest(UNSET).get_instance()._bridges_item_status(
        Status.PUBLISHED, request=editor_request
    )

    translator_request = make_request_with_user(rf, translator_user)
    with pytest.raises(ValidationError):
        BridgeTest(UNSET).get_instance()._bridges_item_status(
            Status.PUBLISHED, request=translator_request
        )

    BridgeTest(UNSET).get_instance()._bridges_item_status(
        Status.REVIEWING, request=translator_request
    )
