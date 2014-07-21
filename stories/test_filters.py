__author__ = 'dmakhno'



from browser import webdriver_retry
from browser.session import with_gui
from qubell.api.private.manifest import Manifest
from stories import base, eventually


class SortingTests(base.BaseTestCase):

    def test(self): pass

    @classmethod
    def setUpClass(cls):
        super(SortingTests, cls).setUpClass()
        first_env = cls.organization.environment(name="first")

        appGreen = cls.organization.application(name="Green " + cls.__name__, manifest=Manifest(content='''
launch:
  steps: []'''))
        appGray = cls.organization.application(name="Gray " + cls.__name__, manifest=Manifest(content='''
launch:
  steps:
    wait:
      action: wait
      parameters:
        delay: 60'''))
        appRed = cls.organization.application(name="Red " + cls.__name__, manifest=Manifest(content='''
launch:
  parameters:
    z:
      default: a string
  steps:
    wait:
      action: wait
      parameters:
        delay: "{$.z}"
        '''))
        cls.apps = [appGreen, appGray, appRed]

        lime = appGreen.create_revision(name="Lime", instance=None)
        chlorophyll = appGreen.create_revision(name="Chlorophyll", instance=None)

        graphite = appGray.create_revision(name="Graphite", instance=None)

        instances = []
        instances.append(appGreen.launch(name="1 Green", environment=first_env))
        instances.append(appGreen.launch(name="2' Green ZYX", revision=lime))
        instances[-1].unstar()
        instances.append(appGreen.launch(name="2' Green ABC", revision=lime))
        instances[-1].unstar()
        instances.append(appGreen.launch(name="3 Green", revision=chlorophyll))
        instances.append(appRed.launch(name="1 Red", environment=first_env))
        instances.append(appRed.launch(name="2 Red"))
        instances.append(appGray.launch(name="1 Gray", environment=first_env))
        instances[-1].cancel_command()
        instances.append(appGray.launch(name="2 Gray", revision=graphite))
        instances[-1].cancel_command()

        cls.instances = instances


    @classmethod
    def tearDownClass(cls):
        for instance in cls.instances:
            instance.force_remove()
        for app in cls.apps:
            app.clean()
        super(SortingTests, cls).tearDownClass()