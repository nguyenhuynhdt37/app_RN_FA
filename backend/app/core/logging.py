import sys
from app.core.config import settings
from loguru import logger


def setup_logging() -> None:
    """Configure loguru for structured, leveled output."""
    logger.remove()  # Remove default handler

    level = "DEBUG" if settings.DEBUG else "INFO"

    # Console — human-readable in dev, JSON-like in prod
    if settings.ENVIRONMENT == "development":
        logger.add(
            sys.stdout,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
                "<level>{message}</level>"
            ),
            colorize=True,
        )
    else:
        # Production: JSON-structured for log aggregators (Datadog, CloudWatch, etc.)
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,  # JSON output
        )

    # File sink — always write to a rotating log file
    logger.add(
        "logs/app.log",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        serialize=True,
    )


__all__ = ["logger", "setup_logging"]
