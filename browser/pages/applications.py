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

from . import QubellPage
from selenium.common.exceptions import WebDriverException
from browser import webdriver_retry
from common import OkMixin
from browser.selenium_utils.page import PageBuilder


class ApplicationPage(QubellPage):
    @webdriver_retry(catch_all=True)
    def to_advanced_launch(self):
        self.webdriver.execute_script("document.getElementsByClassName('js-application-advanced-launch')[0].click()")
        return PageBuilder.create_page(ConfigurationPage, action_name="Launch")

    @webdriver_retry(catch_all=True)
    def to_manifest_editor(self):
        self.webdriver.execute_script("""$('.test-application-show-manifest,.js-navigate[href*="/manifests/"]').click()""")
        editor = PageBuilder.create_page(ManifestEditorPage)
        if not editor.on_page():
            raise WebDriverException("Something wrong with JS, cannot get Manifest Editor Page")  # todo: if this used often refactor
        return editor

    def validate_page(self):
        method = lambda webdriver: "/applications/" in webdriver.current_url
        self._wait_page_load(method, "This is not Application Page")
        return self


class ConfigurationPage(QubellPage, OkMixin):
    def __init__(self, webdriver, action_name):
        self.action_name = action_name
        super(ConfigurationPage, self).__init__(webdriver)

    def validate_page(self):
        method = lambda webdriver: self.action_name == webdriver.title
        self._wait_page_load(method, "This is not {0}-Configuration Page".format(self.action_name))
        return self


class ManifestEditorPage(QubellPage):
    @webdriver_retry(catch_all=True)
    def set_content(self, s):
        ms = s.replace("\n", "\\n")
        self.webdriver.execute_script(
            "var editor = ace.edit($('.editor-ace-editor').get(0)); editor.setValue('" + ms + "')")

    def save(self):
        self.webdriver.find_element_by_class_name('js-editor-save').click()

    def validate_manifest(self):
        self.webdriver.find_element_by_class_name('js-editor-validate').click()

    def validate_page(self):
        method = lambda webdriver: "/manifests/" in webdriver.current_url
        self._wait_page_load(method, "This is not Manifest Editor Page")
        return self