import sh
import pytest
import os
import platform
import subprocess
import yaml
from pathlib import Path

from utils import microk8s_enable, wait_for_pod_state, microk8s_disable
from subprocess import CalledProcessError, check_call, check_output
from validators import validate_amd


class TestAddons(object):
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping AMD tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping AMD tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="AMD tests are only relevant in x86 architectures",
    )
    def test_amd(self):
        """
        Sets up amd gpu operator in a gpu capable system. Skip otherwise.

        """
        try:
            print("Enabling amd")
            microk8s_enable("amd")
        except CalledProcessError:
            print("Could not enable amd addon")
            return
        validate_amd()
        try:
            print("Disabling amd")
            microk8s_disable("amd")
        except CalledProcessError:
            print("Could not disable amd addon")
            return