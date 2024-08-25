"""
This file contains the pluggable component for the transport
"""

import requests
from utils import load_configuration

from config_private import APM_PUBLIC_KEY


#
# general configs
#
config = load_configuration()

#
# configs for zipkin transport
# see notes here:
# https://docs.oracle.com/en-us/iaas/application-performance-monitoring/doc/configure-open-source-tracing-systems.html
#
BASE_URL = config["apm_tracing"]["base_url"]
APM_CONTENT_TYPE = config["apm_tracing"]["apm_content_type"]
APM_UPLOAD_ENDPOINT_URL = f"{BASE_URL}/observations/public-span?dataFormat=zipkin&dataFormatVersion=2&dataKey={APM_PUBLIC_KEY}"

# in config.toml we can enable/disable globally tracing
ENABLE_TRACING = config["apm_tracing"]["enable_tracing"]


def http_transport(encoded_span):
    """
    This function gives the pluggable transport
    to communicate with OCI APM using py-zipkin
    """
    result = None

    if ENABLE_TRACING:
        result = requests.post(
            APM_UPLOAD_ENDPOINT_URL,
            data=encoded_span,
            headers={"Content-Type": APM_CONTENT_TYPE},
            timeout=10,
        )
    return result
