# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Bounded metric labels and payload-free structured telemetry."""
import json
import logging
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

LOG = logging.getLogger('inference')


class JsonSpanExporter(SpanExporter):
    def export(self, spans):
        for span in spans:
            LOG.info(json.dumps({
                'event': 'span', 'name': span.name,
                'trace_id': format(span.context.trace_id, '032x'),
                'span_id': format(span.context.span_id, '016x'),
                'parent_span_id': format(span.parent.span_id, '016x') if span.parent else None,
                'duration_ms': (span.end_time - span.start_time) / 1e6,
                'attributes': dict(span.attributes or {}),
            }))
        return SpanExportResult.SUCCESS


class Telemetry:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.requests = Counter('inference_requests_total', 'Completed HTTP requests',
                                ['route', 'status'], registry=self.registry)
        self.duration = Histogram('inference_request_duration_seconds', 'End-to-end HTTP duration',
                                  ['route'], registry=self.registry,
                                  buckets=(.005, .01, .025, .05, .1, .25, .5, 1, 2, 5, 10, 30))
        self.active = Gauge('inference_active_requests', 'Admitted backend requests', registry=self.registry)
        self.rejections = Counter('inference_rejections_total', 'Admission rejections',
                                  ['reason'], registry=self.registry)
        self.provider = TracerProvider()
        self.provider.add_span_processor(SimpleSpanProcessor(JsonSpanExporter()))
        self.tracer = self.provider.get_tracer('inference-gateway')
