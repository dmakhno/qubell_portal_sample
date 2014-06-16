import os
from threading import current_thread
import time
import urllib2

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from . import logger


class WebDriverFactory(object):
    '''
    This class constructs a Selenium Webdriver using settings in the config file.
    This allows you to substitute different webdrivers by changing the config settings
    while keeping your tests using the same webdriver interface.

    Ideally you will not use this directly.  You will normally use WTF_WEBDRIVER_MANAGER.new_driver()
    to create a new instance of webdriver.

    You can extend this class for the purposes of adding support for webdrivers that are not
    currently supported.
    '''

    #    Note: please be sure to uncomment the Unit test and run them manually before
    #    pushing any changes.  This is because they are disabled.  The reason is
    #    because the unit tests for this class can use up billable hours on sauce labs
    #    or open annoying browser windows.


    # CONFIG SETTINGS #
    DRIVER_TYPE_CONFIG = "selenium_type"
    REMOTE_URL_CONFIG = "selenium_remote_url"
    BROWSER_TYPE_CONFIG = "selenium_browser"
    DESIRED_CAPABILITIES_CONFIG = "selenium_desired_capabilities"
    CHROME_DRIVER_PATH = "selenium_chromedriver_path"
    PHANTOMEJS_EXEC_PATH = "selenium_phantomjs_path"
    SELENIUM_SERVER_LOCATION = "selenium_selenium_server_path"
    LOG_REMOTEDRIVER_PROPS = "selenium_log_remote_webdriver_props"

    # BROWSER CONSTANTS #
    HTMLUNIT = "HTMLUNIT"
    HTMLUNITWITHJS = "HTMLUNITWITHJS"
    ANDROID = "ANDROID"
    CHROME = "CHROME"
    FIREFOX = "FIREFOX"
    INTERNETEXPLORER = "INTERNETEXPLORER"
    IPAD = "IPAD"
    IPHONE = "IPHONE"
    OPERA = "OPERA"
    PHANTOMJS = "PHANTOMJS"
    SAFARI = "SAFARI"

    # ENV vars that are used by selenium.
    __SELENIUM_SERVER_JAR_ENV = "SELENIUM_SERVER_JAR"

    def __init__(self, config):
        '''
        Initializer.
        '''

        self._config = config

    def create_webdriver(self, testname=None):
        '''
            Creates an instance of Selenium webdriver based on config settings.
            This should only be called by a shutdown hook.  Do not call directly within
            a test.

            Kwargs:
                testname: Optional test name to pass, this gets appended to the test name
                          sent to selenium grid.

            Returns:
                WebDriver - Selenium webdriver instance.

        '''
        try:
            driver_type = self._config.get(WebDriverFactory.DRIVER_TYPE_CONFIG)
        except:
            print WebDriverFactory.DRIVER_TYPE_CONFIG + " setting is missing from config. Using defaults"
            driver_type = "LOCAL"

        if driver_type == "REMOTE":
            # Create desired capabilities.
            driver = self.__create_remote_webdriver_from_config(testname=testname)
        else:
            # handle as local webdriver
            driver = self.__create_driver_from_browser_config()

        self.post_create(driver)

        return driver

    def post_create(self, driver):
        try:
            driver.maximize_window()
        except:
            # wait a short period and try again.
            time.sleep(5000)
            try:
                driver.maximize_window()
            except Exception as e:
                logger.warn(
                    "Unable to maximize browser window. It may be possible the browser did not instantiate correctly.",
                    e)

    def __create_driver_from_browser_config(self):
        '''
        Reads the config value for browser type.
        '''
        try:
            browser_type = self._config.get(WebDriverFactory.BROWSER_TYPE_CONFIG)
        except KeyError:
            print WebDriverFactory.BROWSER_TYPE_CONFIG + " missing is missing from config file. Using defaults"
            browser_type = WebDriverFactory.FIREFOX

        browser_type_dict = {
            WebDriverFactory.CHROME: lambda: webdriver.Chrome(
                self._config.get(WebDriverFactory.CHROME_DRIVER_PATH)),
            WebDriverFactory.FIREFOX: lambda: webdriver.Firefox(),
            WebDriverFactory.INTERNETEXPLORER: lambda: webdriver.Ie(),
            WebDriverFactory.OPERA: lambda: webdriver.Opera(),
            WebDriverFactory.PHANTOMJS: lambda: self.__create_phantom_js_driver(),
            WebDriverFactory.SAFARI: lambda: self.__create_safari_driver()
        }

        try:
            return browser_type_dict[browser_type]()
        except KeyError:
            raise TypeError("Unsupported Browser Type {0}".format(browser_type))

    def __create_safari_driver(self):
        '''
        Creates an instance of Safari webdriver.
        '''
        # Check for selenium jar env file needed for safari driver.
        if not os.getenv(self.__SELENIUM_SERVER_JAR_ENV):
            # If not set, check if we have a config setting for it.
            try:
                selenium_server_path = self._config.get(self.SELENIUM_SERVER_LOCATION)
                os.environ[self.__SELENIUM_SERVER_JAR_ENV] = selenium_server_path
            except KeyError:
                raise RuntimeError("Missing selenium server path config {0}.".format(self.SELENIUM_SERVER_LOCATION))

        return webdriver.Safari()

    def __create_phantom_js_driver(self):
        '''
        Creates an instance of PhantomJS driver.
        '''
        try:
            return webdriver.PhantomJS(executable_path=self._config.get(self.PHANTOMEJS_EXEC_PATH),
                                       service_args=['--ignore-ssl-errors=true'])
        except KeyError:
            return webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])


    def __create_remote_webdriver_from_config(self, testname=None):
        '''
        Reads the config value for browser type.
        '''
        browser_type = self._config.get(WebDriverFactory.BROWSER_TYPE_CONFIG)
        remote_url = self._config.get(WebDriverFactory.REMOTE_URL_CONFIG)

        browser_constant_dict = {WebDriverFactory.HTMLUNIT: DesiredCapabilities.HTMLUNIT,
                                 WebDriverFactory.HTMLUNITWITHJS: DesiredCapabilities.HTMLUNITWITHJS,
                                 WebDriverFactory.ANDROID: DesiredCapabilities.ANDROID,
                                 WebDriverFactory.CHROME: DesiredCapabilities.CHROME,
                                 WebDriverFactory.FIREFOX: DesiredCapabilities.FIREFOX,
                                 WebDriverFactory.INTERNETEXPLORER: DesiredCapabilities.INTERNETEXPLORER,
                                 WebDriverFactory.IPAD: DesiredCapabilities.IPAD,
                                 WebDriverFactory.IPHONE: DesiredCapabilities.IPHONE,
                                 WebDriverFactory.OPERA: DesiredCapabilities.OPERA,
                                 WebDriverFactory.SAFARI: DesiredCapabilities.SAFARI,
                                 WebDriverFactory.PHANTOMJS: DesiredCapabilities.PHANTOMJS}

        try:
            desired_capabilities = browser_constant_dict[browser_type].copy()
        except KeyError:
            raise TypeError("Unsupported Browser Type {0}".format(browser_type))

        # Get additional desired properties from config file and add them in.
        other_desired_capabilities = self._config.get(WebDriverFactory.DESIRED_CAPABILITIES_CONFIG, {})

        for prop in other_desired_capabilities:
            value = other_desired_capabilities[prop]

            if type(other_desired_capabilities[prop]) is dict:
                # do some recursive call to flatten this setting.
                self.__flatten_capabilities(desired_capabilities, prop, other_desired_capabilities[prop])
            else:  # Handle has a single string value.
                if isinstance(value, basestring):
                    desired_capabilities[prop] = value

                elif prop == "version":  # Version is specified as a string, but we'll allow user to use an int for convenience.
                    desired_capabilities[prop] = str(value)

                else:
                    desired_capabilities[prop] = value

        # Set the test name property if specified in the WTF_TESTNAME var.
        try:
            test_name = self._config.get("TESTNAME")
            desired_capabilities['name'] = test_name
        except KeyError:
            pass  # No test name is specified, use the default.

        # Append optional testname postfix if supplied.
        if testname:
            if desired_capabilities['name']:
                desired_capabilities['name'] += "-" + testname
            else:
                # handle case where name is not specified.
                desired_capabilities['name'] = testname

        # Instantiate remote webdriver.
        driver = webdriver.Remote(
            desired_capabilities=desired_capabilities,
            command_executor=remote_url
        )

        # Log IP Address of node if configured, so it can be used to troubleshoot issues if they occur.
        log_driver_props = str(self._config.get(WebDriverFactory.LOG_REMOTEDRIVER_PROPS, False)).lower() in ["true",
                                                                                                             "yes"]
        if "wd/hub" in remote_url and log_driver_props:
            try:
                grid_addr = remote_url[:remote_url.index("wd/hub")]
                info_request_response = urllib2.urlopen(grid_addr + "grid/api/testsession?session=" + driver.session_id,
                                                        "", 5000)
                node_info = info_request_response.read()
                logger.info("RemoteWebdriver using node: " + str(node_info).strip())
            except:
                # Unable to get IP Address of remote webdriver.
                # This happens with many 3rd party grid providers as they don't want you accessing info on nodes on
                # their internal network.
                pass

        return driver
        # End of method.

    def __flatten_capabilities(self, desired_capabilities, prefix, setting_group):
        for key in setting_group.keys():
            if type(setting_group[key]) is dict:
                # Do recursive call
                self.__flatten_capabilities(desired_capabilities, prefix + "." + key, setting_group[key])
            else:
                value = setting_group[key]
                if isinstance(value, basestring):
                    desired_capabilities[prefix + "." + key] = value
                else:
                    desired_capabilities[prefix + "." + key] = str(value)


class WebDriverManager(object):
    '''
    Provides Singleton instance of Selenium WebDriver based on
    config settings.

    Reason we don't make this a Utility class that provides a singleton
    of the WebDriver itself is so we can allow that piece to be mocked
    out to assist in unit testing framework classes that may use this.
    '''

    "Config setting to reuse browser instances between WebdriverManager.new_driver() calls."
    REUSE_BROWSER = "selenium_reusebrowser"

    "Config setting to automatically tear down webdriver upon exiting the main script."
    SHUTDOWN_HOOK_CONFIG = "selenium_shutdown_hook"

    "Config setting to use new webdriver instance per thread."
    ENABLE_THREADING_SUPPORT = "selenium_threaded"

    def __init__(self, webdriver_factory, config):
        '''
        Initializer

        Kwargs:
            webdriver_factory (WebDriverFactory): Override default webdriver factory.
            config (ConfigReader): Override default config reader.

        '''
        self.__webdriver = {}  # Object with channel as a key
        self.__registered_drivers = {}

        self.__use_shutdown_hook = config.get(WebDriverManager.SHUTDOWN_HOOK_CONFIG, True)
        self.__reuse_browser = config.get(WebDriverManager.REUSE_BROWSER, True)
        self.__enable_threading_support = config.get(WebDriverManager.ENABLE_THREADING_SUPPORT, False)

        self._webdriver_factory = webdriver_factory

    def prepare_hook(self, driver):
        """
        Attempt to get the browser to a pristine state as possible when we are
        reusing this for another test.
        If reuse browser is set, we'll avoid closing it and just clear out the cookies,
        and reset the location.
        Hook allows to override this behaviour
        """
        driver.delete_all_cookies()
        driver.get("about:blank")  # check to see if webdriver is still responding

    def clean_up_webdrivers(self):
        '''
        Clean up webdrivers created during execution.
        '''
        try:
            if self.__use_shutdown_hook:
                for key in self.__registered_drivers.keys():
                    for driver in self.__registered_drivers[key]:
                        try:
                            driver.quit()
                        except:
                            pass
        except:
            pass


    def close_driver(self):
        """
        Close current instance of webdriver.
        """
        channel = self.__get_channel()
        driver = self.__get_driver_for_channel(channel)
        if not self.__reuse_browser and driver:
            try:
                driver.quit()
            except:
                pass

            self.__unregister_driver(channel)
            if driver in self.__registered_drivers[channel]:
                self.__registered_drivers[channel].remove(driver)

    def get_driver(self):
        '''
        Get an already running instance of webdriver. If there is none, it will create one.

        Returns:
            WebDriver - Selenium Webdriver instance.

        '''
        return self.__get_driver_for_channel(self.__get_channel()) or self.new_driver()

    def is_driver_available(self):
        '''
        Check if a webdriver instance is created.

        Returns:
            bool - True, webdriver is available; False, webdriver not yet initialized.

        '''
        channel = self.__get_channel()
        try:
            return self.__webdriver[channel] != None
        except:
            return False


    def new_driver(self, testname=None):
        '''
        Used at a start of a test to get a new instance of webdriver.  If the
        'resuebrowser' setting is true, it will use a recycled webdriver instance.

        Kwargs:
            testname (str) - Optional test name to pass to Selenium Grid.

        Returns:
            Webdriver - Selenium Webdriver instance.

        '''
        channel = self.__get_channel()

        # Get reference for the current driver.
        driver = self.__get_driver_for_channel(channel)

        if self.__reuse_browser:

            if not driver:
                driver = self._webdriver_factory.create_webdriver(testname=testname)
                self.prepare_hook(driver)
                # Register webdriver so it can be retrieved by the manager and cleaned up after exit.
                self.__register_driver(channel, driver)
            else:
                try:
                    self.prepare_hook(driver)
                except:
                    # In the case the browser is unhealthy, we should kill it and serve a new one.
                    try:
                        if driver.is_online():
                            logger.debug("Closing webdriver for thread due to unhealthy: ", channel)
                            driver.quit()
                    except:
                        pass

                    driver = self._webdriver_factory.create_webdriver(testname=testname)
                    self.__register_driver(channel, driver)

        else:
            # Attempt to tear down any existing webdriver.
            if driver:
                try:
                    logger.debug("Closing webdriver for thread: ", channel)
                    driver.quit()
                except:
                    pass
            self.__unregister_driver(channel)
            driver = self._webdriver_factory.create_webdriver(testname=testname)
            self.prepare_hook(driver)
            self.__register_driver(channel, driver)

        return driver
        # End of new_driver method.


    def __register_driver(self, channel, webdriver):
        "Register webdriver to a channel."

        # Add to list of webdrivers to cleanup.
        if not self.__registered_drivers.has_key(channel):
            self.__registered_drivers[channel] = []  # set to new empty array

        self.__registered_drivers[channel].append(webdriver)

        # Set singleton instance for the channel
        self.__webdriver[channel] = webdriver


    def __unregister_driver(self, channel):
        "Unregister webdriver"
        driver = self.__get_driver_for_channel(channel)

        if self.__registered_drivers.has_key(channel) and driver in self.__registered_drivers[channel]:
            self.__registered_drivers[channel].remove(driver)

        self.__webdriver[channel] = None


    def __get_driver_for_channel(self, channel):
        "Get webdriver for channel"
        try:
            return self.__webdriver[channel]
        except:
            return None


    def __get_channel(self):
        "Get the channel to register webdriver to."
        return current_thread().ident if self.__enable_threading_support else 0

    def __del__(self):
        "Deconstructor, call cleanup drivers."
        self.clean_up_webdrivers()
