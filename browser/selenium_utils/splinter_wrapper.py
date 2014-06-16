from selenium.webdriver.support.wait import WebDriverWait
from splinter.cookie_manager import CookieManagerAPI
from splinter.driver.webdriver import BaseWebDriver
from splinter.driver.webdriver.remote import WebDriverElement as RemoteWebDriverElement

from webdriver import WebDriverFactory


class SplinterDriver(BaseWebDriver):
    """
    Wraps existing webdriver and allows to use splinter api
    """
    driver_name = "Remote webdriver wrapper"

    def __init__(self, existing_driver, wait_time=2):
        self.driver = existing_driver
        self.element_class = ExWebDriverElement
        self._cookie_manager = CookieManagerAPI()
        super(SplinterDriver, self).__init__(wait_time)

    def wait(self, method, wait_time=2):
        return WebDriverWait(self.driver, wait_time).until(method)


class ExWebDriverElement(RemoteWebDriverElement):
    def as_select(self):
        """
        Converts WebElement to Select object, not splinter part, because WebDriver specific
        """
        from selenium.webdriver.support.ui import Select

        return Select(self._element)

    @property
    def selected_text(self):
        return self.as_select().first_selected_option.text


class SplinterFactory(WebDriverFactory):
    """
    Injects splinter driver into instance of webdriver.
    Hacky, however simplifies conversions
    """

    def post_create(self, driver):
        super(SplinterFactory, self).post_create(driver)
        driver.splinter = SplinterDriver(driver)