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

from functools import wraps
import unittest
import sys
import inspect

from qubell.api.private.application import Application
from qubell.api.private.instance import Instance

from browser import CONFIGS, WD_MANAGER, do_and_ignore
from browser.selenium_utils.screenshot import ScreenshotCapturer
from pages.applications import ApplicationPage
from selenium_utils.page import PageBuilder
from pages.instances import InstancePage
from stories import qubell_config


class Site(object):
    def __init__(self, driver, splinter):
        self.driver = driver
        self.webdriver = driver
        self.splinter = splinter

    def navigate(self, item):
        if (type(item) is Instance):
            instance = item
            instanceId = instance.instanceId
            organizationId = instance.application.organizationId
            self.driver.get(qubell_config['tenant'] + "/organizations/" + organizationId + "/instances/" + instanceId)
            return self.instance_page()
        if (type(item) is Application):
            application = item
            applicationId = application.applicationId
            organizationId = application.organization.organizationId
            self.driver.get(qubell_config['tenant'] + "/organizations/" + organizationId + "/applications/" + applicationId)
            return self.application_page()

        raise AttributeError("Item {0} of {1} is not supported for navigation.".format(str(item), type(item)))

    @staticmethod
    def instance_page():
        return PageBuilder.create_page(InstancePage)

    @staticmethod
    def application_page():
        return PageBuilder.create_page(ApplicationPage)


def skip_if_turned_off(testcase):
    if str(CONFIGS.get("selenium_active", False)).lower() not in ("yes", "true", "t", "1"):
        name = unicode(type(testcase).__name__) + u"_" + unicode(testcase._testMethodName)
        raise unittest.SkipTest(name + " skipped due to selenium turned off")


def with_gui():
    def wrapper(func):

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            self = args[0]
            skip_if_turned_off(self)

            driver = WD_MANAGER.new_driver()
            capture = ScreenshotCapturer(WD_MANAGER, CONFIGS) #almost as wathcer
            session = Site(driver, driver.splinter)

            spec = inspect.getargspec(func)[0]
            for v in ["site", "session", "gui"]:
                if v in spec:
                    kwargs[v] = session

            try:
                func(*args, **kwargs)
            except AssertionError as e:
                capture.on_test_failure(self, None, e)
                #raise for next, to have proper place of issue. (2nd element means traceback in returned tuple
                tb = sys.exc_info()[2].tb_next
                raise e, None, tb
            except Exception as e:
                capture.on_test_error(self, None, e)
                tb = sys.exc_info()[2].tb_next
                raise e, None, tb
            finally:
                do_and_ignore(lambda: WD_MANAGER.close_driver())

        return wrapped_func

    return wrapper