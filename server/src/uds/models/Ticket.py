# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Virtual Cable S.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Virtual Cable S.L. nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
.. moduleauthor:: Adolfo Gómez, dkmaster at dkmon dot com
'''

from __future__ import unicode_literals

__updated__ = '2015-03-23'

from django.db import models

from uds.models.UUIDModel import UUIDModel
from uds.models.Util import getSqlDatetime
import datetime


import pickle


import base64
import logging

logger = logging.getLogger(__name__)


class TicketStore(UUIDModel):
    '''
    Image storing on DB model
    This is intended for small images (i will limit them to 128x128), so storing at db is fine

    '''

    stamp = models.DateTimeField()  # Date creation or validation of this entry
    validity = models.IntegerField(default=60)  # Duration allowed for this ticket to be valid, in seconds

    data = models.BinaryField()  # Associated ticket data

    class Meta:
        '''
        Meta class to declare the name of the table at database
        '''
        db_table = 'uds_tickets'
        app_label = 'uds'

    @staticmethod
    def create(data, validity=60):
        return TicketStore.objects.create(stamp=getSqlDatetime(), data=pickle.dumps(data), validity=validity).uuid

    @staticmethod
    def get(uuid):
        try:
            t = TicketStore.objects.get(uuid=uuid)
            if datetime.timedelta(seconds=t.validity) + t.stamp < getSqlDatetime():
                raise Exception('Not valid anymore')
            return pickle.loads(t.data)
        except TicketStore.DoesNotExist:
            raise Exception('Does not exists')

    @staticmethod
    def revalidate(uuid, validity=None):
        try:
            t = TicketStore.objects.get(uuid=uuid)
            t.stamp = getSqlDatetime()
            if validity is not None:
                t.validity = validity
            t.save()
        except TicketStore.DoesNotExist:
            raise Exception('Does not exists')