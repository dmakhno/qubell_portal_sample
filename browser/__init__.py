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

import logging
import os

from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from qubell.api.tools import retry
from selenium_utils.page import PageBuilder
from selenium_utils import read_utils_config
from selenium_utils.screenshot import WebScreenShotUtil
from selenium_utils.splinter_wrapper import SplinterDriver, SplinterFactory
from qubell.api.provider.router import ROUTER as router
from stories import qubell_config
from stories.base import TestQubell
from selenium_utils.webdriver import WebDriverManager


logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.DEBUG)
logging.getLogger("selenium_utils").setLevel(logging.DEBUG)


def do_and_ignore(lambda_func):
    """
    Perform the given function, but only log the error that's printed out.
    Use this function to wrap method calls you would normally do in a try/raise
    block, but do not care about the results.

    Args:
        lambda_func (function) : Lambda function to execute.

    Returns:
        Returns same return as the lambda statement.  Otherwise returns None

    Usage::

        do_and_ignore(lambda: driver.find_element_by_id("logoutButton").click())

    is equivalent to::

        try:
            driver.find_element_by_id("logoutButton").click()
        except Exception as e:
            print e

    This function is useful for wrapping cleanup calls, since it'll ignore any errors
    and keeps the test moving along.

    """
    try:
        return lambda_func()
    except Exception as e:
        try:
            print e
        except:
            print "unknown error"
        return None


def webdriver_retry(catch_all=False):
    """
    Method decorator, that retries action if WebDriver exception appeared
    Note: 'sum([delay*backoff**i for i in range(tries)])' ~= 11 seconds
    :return:
    """

    return retry(tries=60, delay=0.1, backoff=1.02, retry_exception=exceptions.WebDriverException if catch_all else (
        exceptions.NoSuchElementException, exceptions.StaleElementReferenceException))


__browser_path = os.path.dirname(os.path.realpath(__file__))

CONFIGS = read_utils_config(os.path.join(__browser_path, 'configs/default.yaml'))


class QubellWebDriverManager(WebDriverManager):
    def prepare_hook(self, driver):

        driver.delete_all_cookies()
        try:
            driver.get(qubell_config['tenant'] + '/404')
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
        except (TimeoutException, exceptions.NoAlertPresentException):
            pass
        # noinspection PyStatementEffect
        TestQubell.platform
        play_session = 'PLAY_SESSION'
        cook = router._cookies[play_session]
        driver.add_cookie({'name': play_session, 'value': cook})
        if not driver.get_cookie(play_session):
            from selenium_utils import logger

            logger.debug("Cookie was not set, trying again")
            driver.add_cookie({'name': play_session, 'value': cook})
        driver.implicitly_wait(10)


WD_MANAGER = QubellWebDriverManager(SplinterFactory(CONFIGS), CONFIGS)
WebScreenShotUtil.screenshot_root = __browser_path
PageBuilder.webdriver_provider = WD_MANAGER