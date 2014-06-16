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

import re
from browser import webdriver_retry

from browser.selenium_utils.page import Page

class QubellPage(Page):
    def get_ids(self):
        """
        Allows to build simple communication among ui and api
        Returns:
          tuple : first orgId, second is context related, and maybe missed
        """
        return tuple(re.findall("[A-Fa-f0-9]{24}", self.webdriver.current_url))

    title_field = lambda self: self.webdriver.find_element_by_class_name('js-navigation-title')

    @property
    @webdriver_retry()
    def title(self):
        return self.title_field().text