"""
pipeline default settings
"""

# pipeline template context module, to use this, you need
#   1) config PIPELINE_TEMPLATE_CONTEXT in your django settings, such as
#       PIPELINE_TEMPLATE_CONTEXT = 'home_application.utils.get_template_context'
#   2) define get_template_context function in your app, which show accept one arg, such as
#         def get_template_context(obj):
#             context = {
#                 'biz_cc_id': '1',
#                 'biz_cc_name': 'test1',
#             }
#             if obj is not None:
#                 context.update({'template': '1'})
#             return context
PIPELINE_TEMPLATE_CONTEXT = ''
PIPELINE_INSTANCE_CONTEXT = ''
PIPELINE_ENGINE_ADAPTER_API = 'pipeline.service.pipeline_engine_adapter.adapter_api'
