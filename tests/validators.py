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

def validate_amd_gpu():
    """
    Validate AMD GPU by running a simple test pod that runs 'amd-smi' and checks output.
    """

    if platform.machine() != "x86_64":
        print("GPU tests are only relevant on x86 architectures")
        return

    namespace = "default"
    test_pod_name = "amd-smi"
    smi_manifest = TEMPLATES / "amd-smi.yaml"

    existing_pods = kubectl(f"get po {test_pod_name} -n {namespace}")
    if test_pod_name in existing_pods:
        kubectl(f"delete po {test_pod_name} -n {namespace}")
        time.sleep(10)

    kubectl(f"apply -f {smi_manifest}")
    wait_for_pod_state(test_pod_name, namespace, "Succeeded", timeout_insec=600)

    logs = kubectl(f"logs pod/{test_pod_name} -n {namespace}")

    passed = "AMDSMI Tool" in logs and "GPU" in logs and "ROCm version" in logs
    assert passed
