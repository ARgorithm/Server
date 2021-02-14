"""ARgorithm execution based metrics management
"""
import sys
import time
import json
from prometheus_client import Counter, Gauge, Histogram, Summary

EXECUTION_REQUESTS = Counter(
    "execution_requests_total",
    "Total count of requests by argorithm_id and parameters",
    ["argorithm_id","parameters"]
)

EXECUTION_RESPONSES = Counter(
    "execution_responses_total",
    "Total count of responses by argorithm_id, parameters and status.",
    ["argorithm_id","status"]
)

TIME_BUCKETS = [0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000]

EXECUTION_PROCESSING_TIME = Histogram(
    "execution_processing_time_milliseconds",
    "Execution processing time by path in milliseconds",
    ["argorithm_id","status"],
    buckets=TIME_BUCKETS
)

RESPONSE_BUCKETS = [ x/100 for x in range(0,2048,256)]

EXECUTION_RESPONSE_SIZE = Histogram(
    "execution_response_size_bytes",
    "Execution response sizes by argorithm_id",
    ['argorithm_id'],
    buckets=RESPONSE_BUCKETS
)

class PerformanceMonitor:
    """Create metrics based on argorithm execution performance
    """
    def __init__(self):
        pass

    def start_execution(self,data):
        """Updates metrics related to start of execution

        Args:
            data (ExecutionRequest): The request specifics as sent by the user
        """
        parameters = "DEFAULT"
        if data['parameters']:
            parameters = "PROVIDED"
        EXECUTION_REQUESTS.labels(data['argorithmID'],parameters).inc()

    def end_execution(self,data,status,output,time_taken):
        """Updates metrics when execution ends

        Args:
            data (ExecutionRequest): The request specifics as sent by the user
            status (string): String literal defining the status of execution {NORMAL|CACHE|REDIRECT|ERROR}
            output (list): list of states generated
            time_taken (int): time taken in milliseconds
        """
        parameters = "DEFAULT"
        if data['parameters']:
            parameters = "PROVIDED"
        EXECUTION_RESPONSES.labels(data['argorithmID'],status).inc()
        if status != "ERROR":
            EXECUTION_PROCESSING_TIME.labels(data['argorithmID'],status).observe(time_taken)
            val = sys.getsizeof(json.dumps(output)) / 1024
            EXECUTION_RESPONSE_SIZE.labels(data['argorithmID']).observe(val)
