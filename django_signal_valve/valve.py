import logging
import traceback

from .models import Signal

logger = logging.getLogger(__name__)

_valve_function = None


def set_valve_function(func):
    if _valve_function is not None:
        raise Exception("valve function can only be set once.")
    global _valve_function
    if not callable(func):
        raise Exception("valve function must be a callable object")
    _valve_function = func


def send(signal_mod, signal_name, **kwargs):
    if not _valve_function():
        try:
            return getattr(signal_mod, signal_name).send(**kwargs)
        except Exception:
            raise
    else:
        Signal.objects.dump(signal_mod.__path__, signal_name, kwargs)
        return None


def open_valve(signal_mod):
    signal_list = Signal.objects.filter(module_path=signal_mod.__path__).order_by("id")
    response = []
    for signal in signal_list:
        try:
            response.append(getattr(signal_mod, signal.name).send(**signal.kwargs))
            signal.delete()
        except Exception as e:
            logger.error('signal(%s - %s) resend failed: %s' %
                         (signal.module_path, signal.name, traceback.format_exc(e)))
    return response
