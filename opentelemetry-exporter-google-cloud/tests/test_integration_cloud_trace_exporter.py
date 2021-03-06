# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import subprocess
import unittest

import grpc
from google.cloud.trace_v2 import TraceServiceClient
from google.cloud.trace_v2.gapic.transports import trace_service_grpc_transport
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import Span, SpanExportResult
from opentelemetry.trace import SpanContext, SpanKind
from opentelemetry.util import time_ns


class BaseExporterIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.project_id = "TEST-PROJECT"

        # Find a free port to spin up our server at.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        self.address = "localhost:" + str(sock.getsockname()[1])
        sock.close()

        # Start the mock server.
        args = ["mock_server", "-address", self.address]
        self.mock_server_process = subprocess.Popen(
            args, stderr=subprocess.PIPE
        )
        # Block until the mock server starts (it will output the address after starting).
        self.mock_server_process.stderr.readline()

    def tearDown(self):
        self.mock_server_process.kill()


class TestCloudTraceSpanExporter(BaseExporterIntegrationTest):
    def test_export(self):
        trace_id = "6e0c63257de34c92bf9efcd03927272e"
        span_id = "95bb5edabd45950f"

        # Create span and associated data.
        resource_info = Resource(
            {
                "cloud.account.id": 123,
                "host.id": "host",
                "cloud.zone": "US",
                "cloud.provider": "gcp",
                "gcp.resource_type": "gce_instance",
            }
        )
        span = Span(
            name="span_name",
            context=SpanContext(
                trace_id=int(trace_id, 16),
                span_id=int(span_id, 16),
                is_remote=False,
            ),
            parent=None,
            kind=SpanKind.INTERNAL,
            resource=resource_info,
            attributes={"attr_key": "attr_value"},
        )

        # pylint: disable=protected-access
        span._start_time = int(time_ns() - (60 * 1e9))
        span._end_time = time_ns()
        span_data = [span]

        # Setup the trace exporter.
        channel = grpc.insecure_channel(self.address)
        transport = trace_service_grpc_transport.TraceServiceGrpcTransport(
            channel=channel
        )
        client = TraceServiceClient(transport=transport)
        trace_exporter = CloudTraceSpanExporter(self.project_id, client=client)

        # Export the spans and verify the results.
        result = trace_exporter.export(span_data)
        self.assertEqual(result, SpanExportResult.SUCCESS)
