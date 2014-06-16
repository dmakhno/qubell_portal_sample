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
from browser.selenium_utils.page import Page


class InstancePage(QubellPage):
    status_field = lambda self: self.webdriver.find_element_by_class_name('js-header-label')

    @property
    @Page.validate()
    def status(self):
        """Gets the text of the element."""
        return self.status_field().text

    def validate_page(self):
        method = lambda webdriver: "/instances/" in webdriver.current_url
        self._wait_page_load(method, "This is not Instance Page")
        return self
