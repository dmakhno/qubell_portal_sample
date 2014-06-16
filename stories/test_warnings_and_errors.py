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

from browser import webdriver_retry
from browser.session import with_gui
from qubell.api.private.manifest import Manifest
from stories import base, eventually


class ManifestEditorTests(base.BaseTestCase):
    def assert_errors_warnings_count(self, webdriver, warnings, errors):
        @webdriver_retry()
        def get_colored_count(color):
            return len(webdriver.find_elements_by_css_selector("pre." + color))

        @eventually(AssertionError)
        def eventually_assert():
            assert get_colored_count('yellow-color') == warnings
            assert get_colored_count('red-color') == errors

        eventually_assert()

        state = webdriver.find_element_by_css_selector(".js-manifest-editor-manifest-state").text
        if warnings == 0 and errors == 0:
            self.assertEquals(state, "The manifest is valid.")
        elif errors > 0:
            self.assertEquals(state, "The manifest is not valid.")
        else:
            self.assertEquals(state, "The manifest is valid, but has warnings.")

    def base_validate_save(self, gui, manifest, warnings, errors):
        editor = gui.navigate(self.app).validate_page().to_manifest_editor().validate_page()
        editor.set_content(manifest)
        editor.validate_manifest()
        self.assert_errors_warnings_count(gui.webdriver, warnings, errors)
        editor.save()
        self.assert_errors_warnings_count(gui.webdriver, warnings, errors)

    @with_gui()
    def test_warnings_and_errors_are_shown(self, gui):
        manifest_with_problems = '''
test:
  steps:
    do: &do
      action: foo
      precedingPhases: [bar]
    do-again: *do
'''
        self.base_validate_save(gui, manifest_with_problems, 2, 2)

    @with_gui()
    def test_warnings_only_are_shown(self, gui):
        manifest_with_warnings = '''
test:
  steps:
    do: &do
      action: wait
      precedingPhases: [abc]
    do2: *do
    do3: *do
'''
        self.base_validate_save(gui, manifest_with_warnings, 3, 0)

    @with_gui()
    def test_the_only_error_is_shown(self, gui):
        not_working_manifest = "test"
        self.base_validate_save(gui, not_working_manifest, 0, 1)
        assert len(gui.webdriver.find_elements_by_css_selector("pre.red-color a")) == 1, "Location of error is missing"

    @with_gui()
    def test_when_correct_nither_errors_warnings(self, gui):
        simplest_manifest = '{}'
        self.base_validate_save(gui, simplest_manifest, 0, 0)


    @classmethod
    def setUpClass(cls):
        super(ManifestEditorTests, cls).setUpClass()
        cls.app = cls.organization.application(name=cls.__name__, manifest=Manifest(content='{}'))

    @classmethod
    def tearDownClass(cls):
        cls.app.delete()
        super(ManifestEditorTests, cls).tearDownClass()


