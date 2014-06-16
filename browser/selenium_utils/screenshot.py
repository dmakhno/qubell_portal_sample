import datetime
import re
import base64
import os

from selenium.webdriver import remote


class ScreenshotCapturer(object):
    @staticmethod
    def generate_screenshot_filename(testcase):
        '''
        Get the class name and timestamp for generating filenames

        Return:
            str - File Name.

        '''
        fname = unicode(type(testcase).__name__) + u"_" + unicode(testcase._testMethodName)
        fname = re.sub(u"[^a-zA-Z_]+", u"_", fname)
        # Trim test case name incase it's too long.
        fname = fname[:100]
        fmt = u'%y-%m-%d_%H.%M.%S_{fname}'
        return datetime.datetime.now().strftime(fmt).format(fname=fname)


    def __init__(self, webdriver_provider, config):
        self.capture_screenshot = config.get("selenium_take_screenshot", True)
        self.annotate_screenshot = config.get("selenium_annotate_screenshot", False)

        self._screenshot_util = WebScreenShotUtil
        self._webdriver_provider = webdriver_provider

    def on_test_failure(self, testcase, test_result, exception):
        """
        On test failure capture screenshot handler.
        """
        name = self.generate_screenshot_filename(testcase) + u"_Fail"
        print "FAIL: " + exception.message
        if self.capture_screenshot:
            self.__take_screenshot_if_webdriver_open__(name)
            if self.annotate_screenshot: self.__annotate_screenshot__(name, exception)


    def on_test_error(self, testcase, test_result, exception):
        """
        On test error, capture screenshot handler.
        """
        name = self.generate_screenshot_filename(testcase) + u"_Error"
        print "ERROR: " + exception.message
        if self.capture_screenshot:
            self.__take_screenshot_if_webdriver_open__(name)
            if self.annotate_screenshot: self.__annotate_screenshot__(name, exception)

    def __annotate_screenshot__(self, name, exception):
        """
        This method puts short error information on screenshot
        """
        assert False, "not implemented"
        # from wtframework.wtf.utils.project_utils import ProjectUtils
        # import os
        # file_location = os.path.join(ProjectUtils.get_project_root(),
        #                              WebScreenShotUtil.SCREEN_SHOT_LOCATION,
        #                              name + ".png")
        #
        # from PIL import Image
        # from PIL import ImageFont
        # from PIL import ImageDraw
        # img = Image.open(file_location)
        # draw = ImageDraw.Draw(img)
        # font = ImageFont.truetype("sans-serif.ttf", 16)
        # draw.text((0, 0),exception.message,(255,255,255),font=font)
        # img.save(file_location)


    def __take_screenshot_if_webdriver_open__(self, name):
        '''
        Take a screenshot if webdriver is open.

        Args:
            testcase: TestCase

        '''
        if self._webdriver_provider.is_driver_available():
            try:
                driver = self._webdriver_provider.get_driver()
                file_location = self._screenshot_util.take_screenshot(driver, name)
                print u"Screenshot taken: {0} for url: {1}".format(name, driver.current_url)
                print u"[[ATTACHMENT|{path}]]".format(path=file_location)  # for jenkins integration
            except Exception as e:
                print u"Unable to take screenshot. Reason: " + e.message + unicode(type(e))


class WebScreenShotUtil():
    '''
    Utilities for taking screenshots in Selenium Webdriver.
    '''
    screenshot_root = ""

    SCREEN_SHOT_LOCATION = "screenshots"
    REFERENCE_SCREEN_SHOT_LOCATION = "reference-screenshots"

    @staticmethod
    def take_screenshot(webdriver, file_name):
        """
        Captures a screenshot.

        Args:
            webdriver (WebDriver) - Selenium webdriver.
            file_name (str) - File name to save screenshot as.

        """
        folder_location = os.path.join(WebScreenShotUtil.screenshot_root,
                                       WebScreenShotUtil.SCREEN_SHOT_LOCATION)

        return WebScreenShotUtil.__capture_screenshot(webdriver, folder_location, file_name + ".png")

    @staticmethod
    def take_reference_screenshot(webdriver, file_name):
        """
        Captures a screenshot as a reference screenshot.

        Args:
            webdriver (WebDriver) - Selenium webdriver.
            file_name (str) - File name to save screenshot as.
        """
        folder_location = os.path.join(WebScreenShotUtil.screenshot_root,
                                       WebScreenShotUtil.REFERENCE_SCREEN_SHOT_LOCATION)

        return WebScreenShotUtil.__capture_screenshot(webdriver, folder_location, file_name + ".png")


    @staticmethod
    def __capture_screenshot(webdriver, folder_location, file_name):
        "Capture a screenshot"
        # Check folder location exists.
        if not os.path.exists(folder_location): os.makedirs(folder_location)

        file_location = os.path.join(folder_location, file_name)

        if isinstance(webdriver, remote.webdriver.WebDriver):
            # If this is a remote webdriver.  We need to transmit the image data
            # back across system boundries as a base 64 encoded string so it can
            # be decoded back on the local system and written to disk.
            base64_data = webdriver.get_screenshot_as_base64()
            screenshot_data = base64.decodestring(base64_data)
            screenshot_file = open(file_location, "wb")
            screenshot_file.write(screenshot_data)
            screenshot_file.close()
        else:
            webdriver.save_screenshot(file_location)

        return file_location