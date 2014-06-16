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

import testtools

from stories import qubell_config, logger, classproperty
from qubell.api.private.common import Auth
from qubell.api.private.platform import QubellPlatform


class TestQubell():
    """
    This class holds platform object.
    Platform is lazy.
    """

    __lazy_platform = None
    context = Auth(user=qubell_config['user'], password=qubell_config['password'], tenant=qubell_config['tenant'])

    @classproperty
    def platform(cls):
        """
        lazy property, to authenticate when needed
        """
        if not cls.__lazy_platform:
            logger.info('Authenticating...')
            cls.__lazy_platform = QubellPlatform.connect(tenant=qubell_config['tenant'], user=qubell_config['user'],
                                                         password=qubell_config['password'])
            logger.info('Authentication succeeded.')
        return cls.__lazy_platform


class BaseTestCase(testtools.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = TestQubell.context
        cls.platform = TestQubell.platform

        organization_name = cls.__name__
        cls.organization = cls.platform.organization(name=organization_name)

        super(BaseTestCase, cls).setUpClass()