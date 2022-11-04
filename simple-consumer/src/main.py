import logging
import time
from os import getenv
from os.path import realpath, dirname

from dotenv import load_dotenv
from redis import Redis


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    root_dir = realpath(dirname(realpath(__file__)) + "/..")
    load_dotenv(dotenv_path=f"{root_dir}/.env")
    logging.basicConfig(level=getenv("LOGLEVEL", "INFO").upper())

    logger.info("")

    env_configs = {
        ("REDIS_HOSTNAME", "redis", True),
        ("REDIS_PORT", "6379", True),
        ("REDIS_STREAM", "my-stream", True),
    }

    config = {}
    for key, default, log in env_configs:
        config[key] = getenv(key, default)
        if log:
            logger.info("%s='%s'", key, str(config[key]))

    redis = Redis(config["REDIS_HOSTNAME"], int(config["REDIS_PORT"]), retry_on_timeout=True)

    last_id = 0
    sleep_ms = 5000
    while True:
        try:
            resp = redis.xread(
                {config["REDIS_STREAM"]: last_id}, count=1, block=sleep_ms
            )
            if resp:
                key, messages = resp[0]
                last_id, data = messages[0]
                logger.info("Received data LAST_ID='%s' data='%s'", last_id, data)

        except ConnectionError as e:
            print("ERROR REDIS CONNECTION: {}".format(e))
            time.sleep(10)
        except KeyboardInterrupt:
            break
