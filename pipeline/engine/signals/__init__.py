# -*- coding: utf-8 -*-

from django.dispatch import Signal

pipeline_ready = Signal(providing_args=['process_id'])
child_process_ready = Signal(providing_args=['child_id'])
process_ready = Signal(providing_args=['parent_id', 'current_node_id', 'call_from_child'])
batch_process_ready = Signal(providing_args=['process_id_list', 'pipeline_id'])
wake_from_schedule = Signal(providing_args=['process_id, activity_id'])
schedule_ready = Signal(providing_args=['schedule_id', 'countdown', 'process_id'])
process_unfreeze = Signal(providing_args=['process_id'])
# activity failed signal
activity_failed = Signal(providing_args=['pipeline_instance', 'pipeline_activity_id'])
