from celery import Celery
from app.core.settings import settings

celery_app = Celery(
    "api_health_checker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND # Может быть rpc://, redis:// или db+postgresql://
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_ignore_result=False, # Устанавливаем в False, если нужно отслеживать результаты задач Celery
    timezone="UTC",
    enable_utc=True,
)

# Автоматическое обнаружение задач в папке tasks (если вынесете их туда)
celery_app.autodiscover_tasks(['app.services', 'app.tasks'])