import os
import sys
from optparse import OptionParser


def parse_args():
    parser = OptionParser()
    parser.add_option('-s', '--settings', default='django_pivot.tests.test_sqlite_settings', help='Define settings.')
    return parser.parse_args()


if __name__ == '__main__':
    options, tests = parse_args()
    os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

    # Local imports because DJANGO_SETTINGS_MODULE needs to be set first
    import django
    from django.test.utils import get_runner
    from django.conf import settings

    if hasattr(django, 'setup'):
        django.setup()

    TestRunner = get_runner(settings)
    runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    sys.exit(runner.run_tests(tests))
