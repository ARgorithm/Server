import sys
import time
import json
from prometheus_client import Counter, Gauge, Histogram, Summary

EXECUTION_REQUESTS = Counter(
    "argorithm_executions_attempts_total",
    "Total count of requests by argorithm_id and parameters",
    ["argorithmID", "parameters"]
)

EXECUTION_RESPONSES = Counter(
    "argorithm_executions_results_total",
    "Total count of responses by argorithm_id, parameters and status.",
    ["argorithm_id", "parameters","status"]
)

EXECUTION_PROCESSING_TIME = Histogram(
    "execution_processing_time_seconds",
    "Histogram of execution processing time by path (in seconds)",
    ["argorithm_id", "parameters","status"],
)

EXECUTION_RESPONSE_SIZE = Summary(
    "execution_response_size_bytes",
    "Summary of execution response sizes by argorithm_id",
    ['argorithm_id','parameters','status']
)

class PerformanceMonitor:
    
    def __init__(self):
        pass

    def start_execution(self,data):
        parameters = "DEFAULT"
        if data['parameters']:
            parameters = "PROVIDED"
        EXECUTION_REQUESTS.labels(data['argorithmID'],parameters).inc()

    def end_execution(self,data,status,output,time_taken):
        parametes = "DEFAULT"
        if data['parameters']:
            parameters = "PROVIDED"
        EXECUTION_RESPONSES.labels(data['argorithmID'],parameters,status).inc()
        if status != "ERROR":
            EXECUTION_PROCESSING_TIME.labels(data['argorithmID'],parameters,status).observe(time_taken)
            val = json.dumps(output)
            EXECUTION_RESPONSE_SIZE.labels(data['argorithmID'],parameters,status).observe(sys.getsizeof(output))

        