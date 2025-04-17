import logging
import logging.handlers
import sys
import os

def setup_logging(
    log_level: int = logging.INFO,
    log_file: str = './app.log',
    log_to_console: bool = True,
    log_to_file: bool = True
):
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    log_format = logging.Formatter(
        '%(asctime)s - %(name)-25s - %(levelname)-10s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        root_logger.addHandler(console_handler)

    if log_to_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as e:
                print(f"Error creating log directory {log_dir}: {e}", file=sys.stderr)

        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,
                backupCount=2,
                encoding='utf-8'
            )
            file_handler.setFormatter(log_format)
            root_logger.addHandler(file_handler)
        except Exception as e:
             print(f"Error setting up file logging to {log_file}: {e}", file=sys.stderr)

    logging.info("Logging configured.")