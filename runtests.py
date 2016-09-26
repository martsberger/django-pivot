import os
import sys
from optparse import OptionParser


def parse_args():
    parser = OptionParser()
    parser.add_option('-s', '--settings', help='Define settings.')
    parser.add_option('-t', '--unittest', help='Define which test to run. Default all.')
    options, args = parser.parse_args()

    if not options.settings:
        parser.print_help()
        sys.exit(1)

    if not options.unittest:
        options.unittest = ['pivot']

    return options

if __name__ == '__main__':
    options = parse_args()
    os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

    # Local imports because DJANGO_SETTINGS_MODULE needs to be set first
    import django
    from django.test.utils import get_runner
    from django.conf import settings

    if hasattr(django, 'setup'):
        django.setup()

    TestRunner = get_runner(settings)
    runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    sys.exit(runner.run_tests([]))
