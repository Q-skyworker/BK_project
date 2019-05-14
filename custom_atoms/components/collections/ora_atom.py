# -*-coding=utf-8-*-

from django.utils.translation import ugettext_lazy as _
from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from ..collections.helper.password_crypt import *
import cx_Oracle

__group_name__ = _(u"Oracle(module)")

class CreateOrclSql(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            user = data.get_one_of_inputs('user')
            account = data.get_one_of_inputs('account')  # "192.168.102.230:1521/orcl"
            password = data.get_one_of_inputs('password')
            choice = data.get_one_of_inputs('choice')
            sql = data.get_one_of_inputs('sql')

            # user = 'system'
            # password = 'Oracle1234'
            # account = '192.168.102.230:1521/orcl'
            # sql = '''select tablespace_name from dba_data_files'''

            # key = user+'/'+password+'@'+account

            db_connect = cx_Oracle.connect(user, password, account)
            db_cursor = db_connect.cursor()
            logger.error(u'ok,connect')

            if choice == 'select':
                db_cursor.execute(sql)
                logger.error(u'sql is ok')
                tgt_result = db_cursor.fetchall()
                logger.error(u'getit')

                data.set_outputs('result', u"执行成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', str(tgt_result))

            elif choice == 'create':
                db_cursor.execute(sql)

                data.set_outputs('result', u"执行成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "OK,create finish")

            else:
                pass

            return True

            # sql = u'''select tablespace_name from dba_data_files'''
            # conn = cx_Oracle.connect(key)
            # cur = conn.cursor()
            # cur.execute(sql)
            # tgt_result = cur.fetchall()


        except Exception,e:
            data.set_outputs('result', u"执行失败")
            data.set_outputs('atom_res', "failed")
            data.set_outputs('message', str(e))
            return False

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数
           return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class CreateVmComponent(Component):
    name = u'执行Oracle语句'
    code = 'create_OrSql'
    bound_service = CreateOrclSql
    form = settings.STATIC_URL + 'custom_atoms/Oracle/create_OracleSql.js'

