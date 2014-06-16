# Copyright (c) 2014 Qubell Inc., http://qubell.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__copyright__ = "Copyright 2014, Qubell.com"

import os
import logging
import atexit

import nose.plugins.attrib
import testtools
import nose

from qubell.api.provider import log_routes_stat
from qubell.api.tools import retry


class classproperty(property):
    """
    Decorator to have class property
    """
    # noinspection PyMethodOverriding
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


atexit.register(log_routes_stat)

logger = logging.getLogger("qubell.stories")
logger.setLevel(logging.DEBUG)


def attr(*args, **kwargs):
    """A decorator which applies the nose and testtools attr decorator
    """

    def decorator(f):
        if 'skip' in args:
            pass
        elif kwargs.has_key('bug') or kwargs.has_key('issue') or 'fail' in args:
            bug_num = kwargs.get('bug') or kwargs.get('issue') or '0000'
            return bug(bug_num)(f)

        else:
            f = testtools.testcase.attr(args)(f)
            return nose.plugins.attrib.attr(*args, **kwargs)(f)

    return decorator


qubell_config = {'user': os.getenv('QUBELL_USER'), 'password': os.getenv('QUBELL_PASSWORD'),
                 'tenant': os.getenv('QUBELL_TENANT', 'http://localhost:9000'), }
cloud_config = {'provider_name': os.getenv('PROVIDER_NAME', 'test-provider'),
                'provider_type': os.getenv('PROVIDER_TYPE', 'aws-ec2'),
                'provider_identity': os.getenv('PROVIDER_IDENTITY', 'FAKE'),
                'provider_credential': os.getenv('PROVIDER_CREDENTIAL', 'FAKE'),
                'provider_region': os.getenv('PROVIDER_REGION', 'us-east-1')}


def require(var, message):
    if not var:
        logger.fatal(message)
        raise KeyError(message)


def eventually(*exceptions):
    """
    Method decorator, that waits when something inside eventually happens
    Note: 'sum([delay*backoff**i for i in range(tries)])' ~= 580 seconds ~= 10 minutes
    :param exceptions: same as except parameter, if not specified, valid return indicated success
    :return:
    """
    return retry(tries=50, delay=0.5, backoff=1.1, retry_exception=exceptions)


require(qubell_config['user'], 'No username provided. Set QUBELL_USER env')
require(qubell_config['password'], 'No password provided. Set QUBELL_PASSWORD env')