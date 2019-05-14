from modbpm import api
from modbpm.logging import modbpm_logger
from modbpm.utils.unique import node_uniqid
from pipeline.core.pipeline import *
from pipeline.core.data.base import DataObject
from pipeline.core.flow.base import SequenceFlow
from pipeline.core.flow.activity import ServiceActivity, SubProcess, Service, StaticIntervalGenerator
from pipeline.core.flow.event import EmptyStartEvent, EmptyEndEvent
from pipeline.core.flow.gateway import ExclusiveGateway, ParallelGateway, ConvergeGateway, Condition
from pipeline.service.modbpm_adapter import modbpm_adapter
from pipeline.components.collections.test import RetryTestService
from pipeline.core.data import context
from pipeline.components.collections.controller import SleepTimerService, PauseService


class BadService(Service):
    def __init__(self):
        super(BadService, self).__init__('sleep service')

    def execute(self, data, parent_data):
        import time
        while True:
            print 'hahahaha'
            time.sleep(3)
        return True

    def outputs_format(self):
        pass


class SleepService(Service):
    def __init__(self):
        super(SleepService, self).__init__('sleep service')

    def execute(self, data, parent_data):
        import time
        time.sleep(5)
        return True

    def outputs_format(self):
        pass


class TestService(Service):
    def __init__(self):
        super(TestService, self).__init__('start service')

    def execute(self, data, parent_data):
        print '##### test service #####'
        return True

    def outputs_format(self):
        pass


class EchoService(Service):
    def __init__(self):
        super(EchoService, self).__init__('echo service')

    def execute(self, data, parent_data):
        print '##### echo service #####'
        for key, value in data.get_inputs().iteritems():
            data.set_outputs(key, value)
        return True

    def outputs_format(self):
        pass


class LogService(Service):
    def __init__(self):
        super(LogService, self).__init__('log service')

    def execute(self, data, parent_data):
        print '##### log service #####'
        modbpm_logger.error(data.get_inputs())
        return True

    def outputs_format(self):
        pass


class ScheduleService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(1)

    def __init__(self):
        super(ScheduleService, self).__init__('test service')
        self.count = 0

    def execute(self, data, parent_data):
        print data.get_inputs()
        return True

    def schedule(self, data, parent_data, callback_data=None):
        print self.count
        self.count += 1
        import time
        time.sleep(1)
        data.set_outputs(self.count, self.count)
        parent_data.set_outputs(self.count, self.count)
        if self.count == 5:
            self.finish_schedule()
        return True

    def outputs_format(self):
        pass


class CallbackService(Service):
    __need_schedule__ = True

    def __init__(self):
        super(CallbackService, self).__init__('test service')
        self.count = 0

    def execute(self, data, parent_data):
        print data.get_inputs()
        return True

    def schedule(self, data, parent_data, callback_data=None):
        print callback_data
        if callback_data.get('finish', ''):
            return True
        return False

    def outputs_format(self):
        pass


def run_pipeline(pipeline):
    api.create_activity(modbpm_adapter.PipelineProcess, args=(pipeline,), identifier_code=pipeline.id)


def get_simple_pipeline():
    start_event_a_id = node_uniqid()
    act_b_id = node_uniqid()
    end_event_c_id = node_uniqid()

    start_event = EmptyStartEvent(start_event_a_id)
    act = ServiceActivity(id=act_b_id, service=RetryTestService(),
                          data=DataObject({'data': '0', 'value2': '2', 'value3': '3', 'timing': 1000}))
    end_event = EmptyEndEvent(end_event_c_id)

    flow_ab = SequenceFlow('ab', start_event, act)
    flow_bc = SequenceFlow('bc', act, end_event)

    start_event.outgoing.add_flow(flow_ab)
    act.incoming.add_flow(flow_ab)
    act.outgoing.add_flow(flow_bc)
    end_event.incoming.add_flow(flow_bc)

    spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], data=DataObject({}),
                        context=context.Context({}))
    return Pipeline(node_uniqid(), spec)


def test_simple_pipeline():
    run_pipeline(get_simple_pipeline())


def get_parallel_subprocess_pipeline():
    start_event_a_id = node_uniqid()
    gateway_b_id = node_uniqid()
    act_c_id = node_uniqid()
    act_d_id = node_uniqid()
    sub_pipeline = get_parallel_gateway_test_pipeline()
    act_e_id = sub_pipeline.id
    act_f_id = node_uniqid()
    act_g_id = node_uniqid()
    gateway_h_id = node_uniqid()
    end_event_i_id = node_uniqid()

    start_event_a = EmptyStartEvent(start_event_a_id)
    gateway_b = ParallelGateway(gateway_b_id, gateway_h_id)
    act_c = ServiceActivity(act_c_id, service=SleepService(), data=DataObject({'data': '1'}))
    act_d = ServiceActivity(act_d_id, service=SleepService(), data=DataObject({'data': '1'}))
    act_e = SubProcess(act_e_id, pipeline=sub_pipeline)
    act_f = ServiceActivity(act_f_id, service=SleepService(), data=DataObject({'node_1': 'd'}))
    act_g = ServiceActivity(act_g_id, service=SleepService(), data=DataObject({'node_2': 'd'}))
    gateway_h = ConvergeGateway(gateway_h_id)
    end_event_i = EmptyEndEvent(end_event_i_id)

    flow_ab = SequenceFlow('ab', start_event_a, gateway_b)

    flow_bc = SequenceFlow('bc', gateway_b, act_c)
    flow_bd = SequenceFlow('bd', gateway_b, act_d)
    flow_be = SequenceFlow('be', gateway_b, act_e)

    flow_cf = SequenceFlow('cf', act_c, act_f)
    flow_dg = SequenceFlow('dg', act_d, act_g)

    flow_fh = SequenceFlow('fh', act_f, gateway_h)
    flow_gh = SequenceFlow('gh', act_g, gateway_h)
    flow_eh = SequenceFlow('eh', act_e, gateway_h)

    flow_hi = SequenceFlow('hi', gateway_h, end_event_i)

    start_event_a.outgoing.add_flow(flow_ab)
    gateway_b.incoming.add_flow(flow_ab)

    gateway_b.outgoing.add_flow(flow_bc)
    gateway_b.outgoing.add_flow(flow_bd)
    gateway_b.outgoing.add_flow(flow_be)
    act_c.incoming.add_flow(flow_bc)
    act_d.incoming.add_flow(flow_bd)
    act_e.incoming.add_flow(flow_be)

    act_c.outgoing.add_flow(flow_cf)
    act_d.outgoing.add_flow(flow_dg)
    act_e.outgoing.add_flow(flow_eh)

    act_f.incoming.add_flow(flow_cf)
    act_g.incoming.add_flow(flow_dg)
    act_f.outgoing.add_flow(flow_fh)
    act_g.outgoing.add_flow(flow_gh)

    gateway_h.incoming.add_flow(flow_fh)
    gateway_h.incoming.add_flow(flow_gh)
    gateway_h.incoming.add_flow(flow_eh)
    gateway_h.outgoing.add_flow(flow_hi)

    end_event_i.incoming.add_flow(flow_hi)

    spec = PipelineSpec(start_event_a, end_event_i,
                        [flow_ab,
                         flow_bc,
                         flow_bd,
                         flow_be,
                         flow_cf,
                         flow_dg,
                         flow_fh,
                         flow_gh,
                         flow_eh],
                        [act_c, act_d, act_e, act_f, act_g],
                        [gateway_b, gateway_h], data=DataObject({}),
                        context=context.Context(act_outputs={
                        }, output_key=[]))
    return Pipeline(node_uniqid(), spec)


def get_subprocess_pipeline():
    def subprocess():
        start_event_a_id = node_uniqid()
        act_b_id = node_uniqid()
        end_event_c_id = node_uniqid()

        start_event = EmptyStartEvent(start_event_a_id)
        act = ServiceActivity(act_b_id, service=RetryTestService(),
                              data=DataObject({'data': '0'}))
        end_event = EmptyEndEvent(end_event_c_id)

        flow_ab = SequenceFlow('ab', start_event, act)
        flow_bc = SequenceFlow('bc', act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], data=DataObject({}),
                            context=context.Context({}))
        pipeline = Pipeline(node_uniqid(), spec)
        return pipeline

    start_event_a_id = node_uniqid()
    act_b_id = node_uniqid()
    end_event_c_id = node_uniqid()

    start_event = EmptyStartEvent(start_event_a_id)
    sub_pipeline = get_parallel_subprocess_pipeline()
    act = SubProcess(sub_pipeline.id, pipeline=sub_pipeline)
    end_event = EmptyEndEvent(end_event_c_id)

    flow_ab = SequenceFlow('ab', start_event, act)
    flow_bc = SequenceFlow('bc', act, end_event)

    start_event.outgoing.add_flow(flow_ab)
    act.incoming.add_flow(flow_ab)
    act.outgoing.add_flow(flow_bc)
    end_event.incoming.add_flow(flow_bc)

    spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], data=DataObject({}),
                        context=context.Context({}))
    return Pipeline(node_uniqid(), spec)


def test_subprocess_pipeline():
    run_pipeline(get_subprocess_pipeline())


def get_exclusive_gateway_pipeline(result):
    start_event_a_id = node_uniqid()
    act_b_id = node_uniqid()
    gateway_c_id = node_uniqid()
    act_d_id = node_uniqid()
    act_e_id = node_uniqid()
    act_f_id = node_uniqid()
    gateway_g_id = node_uniqid()
    end_event_h_id = node_uniqid()

    start_event_a = EmptyStartEvent(start_event_a_id)
    b_act = ServiceActivity(act_b_id, service=EchoService(), data=DataObject({'a': 3}))
    c_gateway = ExclusiveGateway(gateway_c_id, gateway_g_id)
    d_act = ServiceActivity(act_d_id, service=LogService(), data=DataObject({'node': 'd'}))
    e_act = ServiceActivity(act_e_id, service=EchoService(), data=DataObject({'node': 'e'}))
    f_act = ServiceActivity(act_f_id, service=TestService(), data=DataObject({'node': 'f'}))
    g_gateway = ConvergeGateway(gateway_g_id)
    end_event_h = EmptyEndEvent(end_event_h_id)

    ab_flow = SequenceFlow('ab', start_event_a, b_act)
    bc_flow = SequenceFlow('bc', b_act, c_gateway)
    cd_flow = SequenceFlow('cd', c_gateway, d_act)
    ce_flow = SequenceFlow('ce', c_gateway, e_act)
    cf_flow = SequenceFlow('cf', c_gateway, f_act)
    dg_flow = SequenceFlow('dg', d_act, g_gateway)
    eg_flow = SequenceFlow('eg', e_act, g_gateway)
    fg_flow = SequenceFlow('fg', f_act, g_gateway)
    gh_flow = SequenceFlow('gh', g_gateway, end_event_h)

    start_event_a.outgoing.add_flow(ab_flow)
    b_act.incoming.add_flow(ab_flow)
    b_act.outgoing.add_flow(bc_flow)
    c_gateway.incoming.add_flow(bc_flow)
    c_gateway.outgoing.add_flow(cd_flow)
    c_gateway.outgoing.add_flow(ce_flow)
    c_gateway.outgoing.add_flow(cf_flow)
    d_act.incoming.add_flow(cd_flow)
    d_act.outgoing.add_flow(dg_flow)
    e_act.incoming.add_flow(ce_flow)
    e_act.outgoing.add_flow(eg_flow)
    f_act.incoming.add_flow(cf_flow)
    f_act.outgoing.add_flow(fg_flow)
    g_gateway.incoming.add_flow(dg_flow)
    g_gateway.incoming.add_flow(eg_flow)
    g_gateway.incoming.add_flow(fg_flow)
    g_gateway.outgoing.add_flow(gh_flow)
    end_event_h.incoming.add_flow(gh_flow)

    c_gateway.add_condition(Condition('result == 1', cd_flow))
    c_gateway.add_condition(Condition('result == 2', ce_flow))
    c_gateway.add_condition(Condition('result == 3', cf_flow))
    spec = PipelineSpec(start_event_a, end_event_h,
                        [ab_flow,
                         bc_flow,
                         cd_flow,
                         ce_flow,
                         cf_flow,
                         dg_flow,
                         eg_flow,
                         fg_flow,
                         gh_flow],
                        [b_act, d_act, e_act, f_act], [c_gateway, g_gateway], data=DataObject({}),
                        context=context.Context(act_outputs={}, scope={'result': result}))
    return Pipeline(node_uniqid(), spec)


def test_exclusive_gateway_pipeline():
    run_pipeline(get_exclusive_gateway_pipeline(1))


def get_parallel_gateway_test_pipeline():
    start_event_a_id = node_uniqid()
    gateway_b_id = node_uniqid()
    act_c_id = node_uniqid()
    act_d_id = node_uniqid()
    act_e_id = node_uniqid()
    act_f_id = node_uniqid()
    act_g_id = node_uniqid()
    gateway_h_id = node_uniqid()
    end_event_i_id = node_uniqid()

    start_event_a = EmptyStartEvent(start_event_a_id)
    gateway_b = ParallelGateway(gateway_b_id, gateway_h_id)
    act_c = ServiceActivity(act_c_id, service=SleepService(), data=DataObject({'data': '1'}))
    act_d = ServiceActivity(act_d_id, service=SleepService(), data=DataObject({'data': '1'}))
    act_e = ServiceActivity(act_e_id, service=SleepService(), data=DataObject({'data': '1'}))
    act_f = ServiceActivity(act_f_id, service=SleepService(), data=DataObject({'node_1': 'd'}))
    act_g = ServiceActivity(act_g_id, service=SleepService(), data=DataObject({'node_2': 'd'}))
    gateway_h = ConvergeGateway(gateway_h_id)
    end_event_i = EmptyEndEvent(end_event_i_id)

    flow_ab = SequenceFlow('ab', start_event_a, gateway_b)

    flow_bc = SequenceFlow('bc', gateway_b, act_c)
    flow_bd = SequenceFlow('bd', gateway_b, act_d)
    flow_be = SequenceFlow('be', gateway_b, act_e)

    flow_cf = SequenceFlow('cf', act_c, act_f)
    flow_dg = SequenceFlow('dg', act_d, act_g)

    flow_fh = SequenceFlow('fh', act_f, gateway_h)
    flow_gh = SequenceFlow('gh', act_g, gateway_h)
    flow_eh = SequenceFlow('eh', act_e, gateway_h)

    flow_hi = SequenceFlow('hi', gateway_h, end_event_i)

    start_event_a.outgoing.add_flow(flow_ab)
    gateway_b.incoming.add_flow(flow_ab)

    gateway_b.outgoing.add_flow(flow_bc)
    gateway_b.outgoing.add_flow(flow_bd)
    gateway_b.outgoing.add_flow(flow_be)
    act_c.incoming.add_flow(flow_bc)
    act_d.incoming.add_flow(flow_bd)
    act_e.incoming.add_flow(flow_be)

    act_c.outgoing.add_flow(flow_cf)
    act_d.outgoing.add_flow(flow_dg)
    act_e.outgoing.add_flow(flow_eh)

    act_f.incoming.add_flow(flow_cf)
    act_g.incoming.add_flow(flow_dg)
    act_f.outgoing.add_flow(flow_fh)
    act_g.outgoing.add_flow(flow_gh)

    gateway_h.incoming.add_flow(flow_fh)
    gateway_h.incoming.add_flow(flow_gh)
    gateway_h.incoming.add_flow(flow_eh)
    gateway_h.outgoing.add_flow(flow_hi)

    end_event_i.incoming.add_flow(flow_hi)

    spec = PipelineSpec(start_event_a, end_event_i,
                        [flow_ab,
                         flow_bc,
                         flow_bd,
                         flow_be,
                         flow_cf,
                         flow_dg,
                         flow_fh,
                         flow_gh,
                         flow_eh],
                        [act_c, act_d, act_e, act_f, act_g],
                        [gateway_b, gateway_h], data=DataObject({}),
                        context=context.Context(act_outputs={
                            act_f_id: {
                                'node_1': 'node_1_heihei'
                            },
                            act_d_id: {
                                'data': 'data_haha'
                            }
                        }, output_key=['node_1_heihei', 'data_haha']))
    return Pipeline(node_uniqid(), spec)


def get_empty_parallel_gateway_test_pipeline():
    start_event_a_id = node_uniqid()
    gateway_b_id = node_uniqid()
    gateway_h_id = node_uniqid()
    end_event_i_id = node_uniqid()

    start_event_a = EmptyStartEvent(start_event_a_id)
    gateway_b = ParallelGateway(gateway_b_id, gateway_h_id)
    gateway_h = ConvergeGateway(gateway_h_id)
    end_event_i = EmptyEndEvent(end_event_i_id)

    flow_ab = SequenceFlow('ab', start_event_a, gateway_b)

    flow_bc = SequenceFlow('bc', gateway_b, gateway_h)
    flow_bd = SequenceFlow('bd', gateway_b, gateway_h)
    flow_be = SequenceFlow('be', gateway_b, gateway_h)

    flow_hi = SequenceFlow('hi', gateway_h, end_event_i)

    start_event_a.outgoing.add_flow(flow_ab)
    gateway_b.incoming.add_flow(flow_ab)

    gateway_b.outgoing.add_flow(flow_bc)
    gateway_b.outgoing.add_flow(flow_bd)
    gateway_b.outgoing.add_flow(flow_be)

    gateway_h.incoming.add_flow(flow_bc)
    gateway_h.incoming.add_flow(flow_bd)
    gateway_h.incoming.add_flow(flow_be)
    gateway_h.outgoing.add_flow(flow_hi)

    end_event_i.incoming.add_flow(flow_hi)

    spec = PipelineSpec(start_event_a, end_event_i,
                        [flow_ab,
                         flow_bc,
                         flow_bd,
                         flow_be],
                        [],
                        [gateway_b, gateway_h], data=DataObject({}),
                        context=context.Context(act_outputs={
                        }, output_key=[]))
    return Pipeline(node_uniqid(), spec)


def test_parallel_gateway_pipeline():
    run_pipeline(get_parallel_gateway_test_pipeline())


def test_simple_schedule_pipeline():
    start_event_a_id = node_uniqid()
    act_b_id = node_uniqid()
    end_event_c_id = node_uniqid()

    start_event = EmptyStartEvent(start_event_a_id)
    act = ServiceActivity(act_b_id, service=ScheduleService(), data=DataObject({}))
    end_event = EmptyEndEvent(end_event_c_id)

    flow_ab = SequenceFlow('ab', start_event, act)
    flow_bc = SequenceFlow('bc', act, end_event)

    start_event.outgoing.add_flow(flow_ab)
    act.incoming.add_flow(flow_ab)
    act.outgoing.add_flow(flow_bc)
    end_event.incoming.add_flow(flow_bc)

    spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], data=DataObject({}),
                        context=context.Context({}))
    pipeline = Pipeline(node_uniqid(), spec)
    run_pipeline(pipeline)


def get_simple_fail_pipeline():
    start_event_a_id = node_uniqid()
    act_b_id = node_uniqid()
    end_event_c_id = node_uniqid()

    start_event = EmptyStartEvent(start_event_a_id)
    act = ServiceActivity(act_b_id, service=RetryTestService(), data=DataObject({'data': '0'}))
    end_event = EmptyEndEvent(end_event_c_id)

    flow_ab = SequenceFlow('ab', start_event, act)
    flow_bc = SequenceFlow('bc', act, end_event)

    start_event.outgoing.add_flow(flow_ab)
    act.incoming.add_flow(flow_ab)
    act.outgoing.add_flow(flow_bc)
    end_event.incoming.add_flow(flow_bc)

    spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], data=DataObject({}),
                        context=context.Context({}))
    return Pipeline(node_uniqid(), spec)


def test_simple_fail_pipeline():
    run_pipeline(get_simple_fail_pipeline())
