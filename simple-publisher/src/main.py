from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_apscheduler import APScheduler
from os import getenv
import secrets
import logging

from time import sleep

from dotenv import load_dotenv
from os.path import realpath, dirname
import socket
from datetime import datetime
import json
from redis import Redis


logger = logging.getLogger(__name__)
root_dir = realpath(dirname(realpath(__file__)) + "/..")
load_dotenv(dotenv_path=f"{root_dir}/.env")
logging.basicConfig(level=getenv("LOGLEVEL", "INFO").upper())

run_port = getenv("RUN_PORT", 80)
run_host = getenv("RUN_HOST", "0.0.0.0")
is_run_debug = getenv('FLASK_DEBUG', "false").lower() in ['true', '1', 't', 'y', 'yes']

logger.info("")

env_configs = {
    ("REDIS_HOSTNAME", "redis", True),
    ("REDIS_PORT", "6379", True),
    ("REDIS_STREAM", "my-stream", True),
}

app = Flask(__name__)
app.config["FLASK_ENV"] = "production" if is_run_debug else "development"
for key, default, log in env_configs:
    app.config[key] = getenv(key, default)
    if log:
        logger.info("%s='%s'", key, str(app.config[key]))

scheduler = BackgroundScheduler()
flask_scheduler = APScheduler(scheduler)
flask_scheduler.init_app(app)

redis = Redis(app.config["REDIS_HOSTNAME"], int(app.config["REDIS_PORT"]), retry_on_timeout=True)

hostname = socket.gethostname()

message_number = 0


def get_ms_time():
    # microsecond
    return datetime.now().microsecond


@app.get("/")
def home():
    return f"Hello World! It's '{get_ms_time()}' and I am host:'{hostname}'"


def detect():
    # Bias towards 0
    detection_options = [0] + [0] + list(range(0, 8))

    # ===Random numbers like an AI detection===
    # fmt: off
    detections = {
        "car": secrets.choice(detection_options),
        "person": secrets.choice(detection_options),
        "cat": secrets.choice(detection_options),
        "dog": secrets.choice(detection_options)
    }
    # fmt: on

    return detections


def send_detections():
    global message_number

    logger.info("")
    logger.info("send_detections: Starting")

    detections = detect()

    message_number = message_number + 1

    message = json.dumps({
        "message_number": message_number,
        "host": hostname,
        "at": get_ms_time(),
        "detections": {
            "car": detections["car"],
            "person": detections["person"],
            "cat": detections["cat"],
            "dog": detections["dog"]
        }
    })
    logger.info(message)

    response = redis.xadd(app.config["REDIS_STREAM"], {"message": message.encode("utf8")})
    logger.info(response)

    sleep_for = secrets.choice(list(range(0, 3)))
    logger.info("send_detections: Sleeping for '%s'", sleep_for)
    sleep(sleep_for)
    logger.info("send_detections: Complete")

    logger.info("")


scheduler.add_job(send_detections, 'interval', seconds=1, max_instances=1)
flask_scheduler.start()

if __name__ == '__main__':
    app.run(debug=is_run_debug, host=run_host, port=run_port)
