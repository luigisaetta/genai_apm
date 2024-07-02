"""
first APM example

this is the one from the blog:
https://blogs.oracle.com/observability/post/oci-apm-python-tracing
"""

import time
from flask import Flask

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span

# customized transport
from transport import http_transport


@zipkin_span(service_name="storefront", span_name="service1-storefront")
def service1():
    """
    a service
    """
    time.sleep(2)
    service2()


@zipkin_span(service_name="catalogue", span_name="service2-catalogue")
def service2():
    """
    a service
    """
    time.sleep(1)


@zipkin_span(service_name="orders", span_name="service3-orders")
def service3():
    """
    a service
    """
    service4()


@zipkin_span(service_name="payment", span_name="service4-payment")
def service4():
    """
    a service
    """
    return


app = Flask(__name__)


@app.route("/tracing")
def apm_tracing():
    """
    start the trace
    """
    with zipkin_span(
        service_name="DemoAPMApp v2",
        span_name="Demo OCI APM App Spans V2",
        transport_handler=http_transport,
        encoding=Encoding.V2_JSON,
        binary_annotations={"oci-input": "This is a Test APM tracing web application"},
        sample_rate=100,  # this is optional and can be used to set custom sample rates
    ):
        service1()
        service3()
    return "This is a Test APM tracing web application"


if __name__ == "__main__":
    app.run(port=8888, debug=False)
