from prometheus_client import Counter, Histogram
from pymongo.monitoring import CommandListener

DB_EVENT_STARTED = Counter(
    "database_event_started",
    "total number of commands given to MongoDB database",
    ["command"]
)

DB_EVENT_FINISHED = Counter(
    "database_event_finished",
    "total number of commands completed by MongoDB database",
    ["command","status"]
)

DB_EVENT_TIME = Histogram(
    "database_event_time",
    "total time taken by commands given to MongoDB database",
    ["command","status"]
)

class DatabaseMonitor(CommandListener):

    def started(self, event):
        DB_EVENT_STARTED.labels(event.command_name).inc()

    def succeeded(self, event):
        DB_EVENT_FINISHED.labels(event.command_name,"success").inc()
        time_taken = event.duration_micros / 1000
        DB_EVENT_TIME.labels(event.command_name,"success").observe(time_taken)

    def failed(self, event):
        DB_EVENT_FINISHED.labels(event.command_name,"failure").inc()
        time_taken = event.duration_micros / 1000
        DB_EVENT_TIME.labels(event.command_name,"failure").observe(time_taken)