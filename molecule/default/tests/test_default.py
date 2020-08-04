import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_apache_is_installed(host):
	apache = host.package("apache2")
	assert apache.is_installed

def test_apache_is_enabled_and_running(host):
	apache = host.service("apache2")
	assert apache.is_running
	assert apache.is_enabled