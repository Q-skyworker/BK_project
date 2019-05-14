# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

MAINTAINERS = 'Maintainers'
PRODUCTPM = 'ProductPm'
DEVELOPER = 'Developer'
TESTER = 'Tester'
OWNER = 'Owner'
COOPERATION = 'Cooperation'
ADMIN = 'Admin'
FUNCTOR = 'Functor'  # 职能化人员
AUDITOR = 'Auditor'

ROLES_DECS = {
    MAINTAINERS: _(u"运维人员"),
    PRODUCTPM: _(u"产品人员"),
    COOPERATION: _(u"合作商"),
    OWNER: _(u"业务创建人"),
    ADMIN: _(u"超级管理员"),
    FUNCTOR: _(u"职能化人员"),
    TESTER: _(u"测试人员"),
    DEVELOPER: _(u"开发人员"),
    AUDITOR: _(u"审计人员"),

}

ALL_ROLES = [
    MAINTAINERS,
    PRODUCTPM,
    DEVELOPER,
    TESTER,
    OWNER,
    ADMIN,
    FUNCTOR,
    AUDITOR,
]


ADMIN_ROLES = [
    MAINTAINERS,
    OWNER,
]

CC_ROLES = [
    MAINTAINERS,
    PRODUCTPM,
    DEVELOPER,
    TESTER,
]

# 默认通知分组
CC_PERSON_GROUP = [
    {"value": role, "text": ROLES_DECS[role]} for role in CC_ROLES
]

DEFAULT_CC_NOTIFY_SET = (
    MAINTAINERS,
)
