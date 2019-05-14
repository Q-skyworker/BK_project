# -*- coding: utf-8 -*-
import threading

import time
from django.core.urlresolvers import resolve, Resolver404, reverse

from common.log import logger
from debug_panel.cache import cache
from debug_panel.middleware import DebugPanelMiddleware, debug_panel


class BKDebugPanelMiddleWare(DebugPanelMiddleware):

    def process_request(self, request):
        """
        Try to match the request with an URL from debug_panel application.

        If it matches, that means we are serving a view from debug_panel,
        and we can skip the debug_toolbar middleware.

        Otherwise we fallback to the default debug_toolbar middleware.
        """

        try:
            res = resolve(request.path_info, urlconf=debug_panel.urls)
        except Resolver404:
            return super(DebugPanelMiddleware, self).process_request(request)

        return res.func(request, *res.args, **res.kwargs)

    def process_response(self, request, response):
        # only valid for superuser
        if not hasattr(request, "user") or not request.user.is_superuser:
            response.set_cookie('djdt', 'hide', 864000)
            return response

        toolbar = self.__class__.debug_toolbars.pop(
            threading.current_thread().ident, None)
        if not toolbar:
            return response

        # Run process_response methods of panels like Django middleware.
        for panel in reversed(toolbar.enabled_panels):
            new_response = panel.process_response(request, response)
            if new_response:
                response = new_response

        # Deactivate instrumentation ie. monkey-unpatch. This must run
        # regardless of the response. Keep 'return' clauses below.
        # (NB: Django's model for middleware doesn't guarantee anything.)
        for panel in reversed(toolbar.enabled_panels):
            panel.disable_instrumentation()

        # Collapse the toolbar by default if SHOW_COLLAPSED is set.
        if toolbar.config['SHOW_COLLAPSED'] and 'djdt' not in request.COOKIES:
            response.set_cookie('djdt', 'hide', 864000)

        # When the toolbar will be inserted for sure, generate the stats.
        for panel in reversed(toolbar.enabled_panels):
            panel.generate_stats(request, response)

        cache_key = "%f" % time.time()
        cache.set(cache_key, toolbar.render_toolbar())

        response['X-debug-data-url'] = request.build_absolute_uri(
            reverse('debug_data', urlconf=debug_panel.urls,
                    kwargs={'cache_key': cache_key}))

        logger.info("django-debug-toolbar: \nrequest_url: {request_url}\n"
                    "debug_url: {debug_url}".format(
                        request_url=request.path,
                        debug_url=response['X-debug-data-url']
                    ))

        return response
