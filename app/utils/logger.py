import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        })

def setup_logger(name="quadroPE"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    has_json_stream_handler = any(
        isinstance(handler, logging.StreamHandler)
        and isinstance(handler.formatter, JSONFormatter)
        for handler in logger.handlers
    )

    if not has_json_stream_handler:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger