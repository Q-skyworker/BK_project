from django.apps import AppConfig


class EngineConfig(AppConfig):
    name = 'pipeline.engine'
    verbose_name = "PipelineEngine"

    def ready(self):
        from pipeline.engine.signals import dispatch
        dispatch.dispatch()

        from django_signal_valve import valve
        from pipeline.engine.models import FunctionSwitch
        valve.set_valve_function(FunctionSwitch.objects.is_frozen)
        FunctionSwitch.objects.init_db()
