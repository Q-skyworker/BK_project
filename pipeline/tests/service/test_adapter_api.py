from django.test import TestCase

from pipeline.service.modbpm_adapter import adapter_api
from modbpm.models import ActivityModel
from modbpm.core import AbstractActivity
from modbpm.states import *


class TestActivity(AbstractActivity):
    pass


class TestAdapterApi(TestCase):
    def setUp(self):
        created_act = ActivityModel.objects.create_activity(TestActivity, args=(), kwargs={})
        created_act.state = CREATED
        created_act.save()
        self.created_act = created_act

        ready_act = ActivityModel.objects.create_activity(TestActivity, args=(), kwargs={})
        ready_act.state = READY
        ready_act.save()
        self.ready_act = ready_act

        revoked_act = ActivityModel.objects.create_activity(TestActivity, args=(), kwargs={})
        revoked_act.state = REVOKED
        revoked_act.save()
        self.revoked_act = ready_act

        suspended_act = ActivityModel.objects.create_activity(TestActivity, args=(), kwargs={})
        suspended_act.state = SUSPENDED
        suspended_act.save()
        self.suspended_act = suspended_act

        blocked_act = ActivityModel.objects.create_activity(TestActivity, args=(), kwargs={})
        blocked_act.state = BLOCKED
        blocked_act.save()
        self.blocked_act = BLOCKED

        failed_act = ActivityModel.objects.create_activity(TestActivity, args=(), kwargs={})
        failed_act.state = FAILED
        failed_act.save()
        self.failed_act = failed_act

    def test_pause_pipeline(self):
        self.assertTrue(adapter_api.pause_pipeline(self.ready_act.identifier_code))
        self.assertFalse(adapter_api.pause_pipeline(self.failed_act.identifier_code))

    def test_revoke_pipeline(self):
        self.assertTrue(adapter_api.revoke_pipeline(self.created_act.identifier_code))
        self.assertFalse(adapter_api.revoke_pipeline(self.failed_act.identifier_code))

    def test_resume_pipeline(self):
        self.assertTrue(adapter_api.resume_pipeline(self.suspended_act.identifier_code))
        self.assertFalse(adapter_api.resume_pipeline(self.revoked_act.identifier_code))

    def test_pause_activity(self):
        self.assertTrue(adapter_api.pause_activity(self.ready_act.identifier_code))
        self.assertFalse(adapter_api.pause_activity(self.failed_act.identifier_code))

    def test_resume_activity(self):
        self.assertTrue(adapter_api.resume_activity(self.suspended_act.identifier_code))
        self.assertFalse(adapter_api.resume_activity(self.revoked_act.identifier_code))

    def test_revoke_activity(self):
        self.assertTrue(adapter_api.revoke_activity(self.created_act.identifier_code))
        self.assertFalse(adapter_api.revoke_activity(self.failed_act.identifier_code))

    def test_retry_activity(self):
        self.assertTrue(adapter_api.retry_activity(self.failed_act.identifier_code))
        self.assertFalse(adapter_api.retry_activity(self.created_act.identifier_code))

    def test_skip_activity(self):
        self.assertTrue(adapter_api.skip_activity(self.failed_act.identifier_code))
