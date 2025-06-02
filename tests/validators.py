import time
import os
import re
import requests
import platform
import yaml
import subprocess
from pathlib import Path

from utils import (
    get_arch,
    kubectl,
    wait_for_pod_state,
    kubectl_get,
    wait_for_installation,
    docker,
    update_yaml_with_arch,
    run_until_success,
    is_multinode,
)

TEMPLATES = Path(__file__).absolute().parent / "templates"
PATCH_TEMPLATES = Path(__file__).absolute().parent / "templates" / "patches"

def validate_amd():
    """
    Validate amd gpu addon.
    """
    wait_for_pod_state(
        pod="",
        namespace="kube-amd-gpu",
        desired_state="status",
        label="control-plane=controller-manager",
        timeout_insec=1500,
    )
    test_template = TEMPLATES / "amd-test.yaml"

    get_pod = kubectl_get("po")
    if "amd-test-pod" in str(get_pod):
        kubectl("delete -f {}".format(test_template))
        time.sleep(30)
    
    kubectl("apply -f {}".format(test_template))
    wait_for_pod_state(
        pod="amd-test-pod",
        namespace="default",
        desired_state="terminated",
    )
    result = kubectl("logs pod/amd-test-pod")
    assert "PASSED" in result
