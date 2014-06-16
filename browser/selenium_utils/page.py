import abc
from functools import wraps

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


class Page(object):
    def __init__(self, webdriver):
        self.webdriver = webdriver

    __metaclass__ = abc.ABCMeta  # needed to make this an abstract class in Python 2.7

    @abc.abstractmethod
    def validate_page(self):
        """Perform checks to validate this page is the correct target page.

        All PageObjects must implement this method.

        Args:
            webdriver (Webdriver) : instance of Selenium Webdriver
        Raises:
            InvalidPageError: Raised when we try to assign the wrong page
            to this page object.  This exception should be raised when a page match
            fails.  Any other exception type would be consider a code failure.
        Returns:
            self: for fluidity

        """
        return

    def on_page(self):
        try:
            self.validate_page()
            return True
        except InvalidPageError:
            return False

    def _wait_page_load(self, method, message):
        try:
            WebDriverWait(self.webdriver, 30).until(method)
        except TimeoutException:
            raise InvalidPageError(message)

    @staticmethod
    def validate():
        """
        Decorator, for page methods, that validate that page is still open
        """

        def wrapper(func):
            @wraps(func)
            def wrapped_func(*args, **kwargs):
                self = args[0]
                assert isinstance(self, Page)
                assert self.on_page()
                return func(*args, **kwargs)

            return wrapped_func

        return wrapper


class PageBuilder(object):

    webdriver_provider = None

    @staticmethod
    def create_page(page_obj_class, **kwargs):
        webdriver = PageBuilder.webdriver_provider.get_driver()
        try:
            page = page_obj_class(webdriver, **kwargs)
            return page
        #        except InvalidPageError:
        #            pass  # This happens when the page fails check.
        #except TypeError:
        #    pass  # this happens when it tries to instantiate the original abstract class.
        except Exception as e:
            # Unexpected exception.
            raise e


class InvalidPageError(Exception):
    '''Thrown when we have tried to instantiate the incorrect page to a PageObject.'''
    pass