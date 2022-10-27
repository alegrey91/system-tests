from systest_utils import TestUtil

from .tests_cases import KubescapeTests, KSMicroserviceTests
from .tests_cases.vulnerability_scanning_tests import VulnerabilityScanningTests
from .tests_cases.ks_vulnerability_scanning_tests import KsVulnerabilityScanningTests


def all_tests_names():
    tests = list()

    tests.extend(TestUtil.get_class_methods(KubescapeTests))
    tests.extend(TestUtil.get_class_methods(VulnerabilityScanningTests))
    tests.extend(TestUtil.get_class_methods(KSMicroserviceTests))
    tests.extend(TestUtil.get_class_methods(KsVulnerabilityScanningTests))
    return tests


def get_test(test_name):

    if test_name in TestUtil.get_class_methods(KubescapeTests):
        return KubescapeTests().__getattribute__(test_name)()
    if test_name in TestUtil.get_class_methods(VulnerabilityScanningTests):
        return VulnerabilityScanningTests().__getattribute__(test_name)()
    if test_name in TestUtil.get_class_methods(KSMicroserviceTests):
        return KSMicroserviceTests().__getattribute__(test_name)()
    if test_name in TestUtil.get_class_methods(KsVulnerabilityScanningTests):
        return KsVulnerabilityScanningTests().__getattribute__(test_name)()


ALL_TESTS = all_tests_names()
