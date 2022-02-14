from typing import Dict, Union

import celery

from ..celeryconf import app
from ..core import JobStatus
from . import events
from .models import ExportFile
from .notifications import send_export_failed_info
from .utils.export import export_gift_cards, export_products


class ExportTask(celery.Task):
    # should be updated when new export task is added
    TASK_NAME_TO_DATA_TYPE_MAPPING = {
        "export-products": "products",
        "export-gift-cards": "gift cards",
    }

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        export_file_id = args[0]
        export_file = ExportFile.objects.get(pk=export_file_id)

        export_file.content_file = None
        export_file.status = JobStatus.FAILED
        export_file.save(update_fields=["status", "updated_at", "content_file"])

        events.export_failed_event(
            export_file=export_file,
            user=export_file.user,
            app=export_file.app,
            message=str(exc),
            error_type=str(einfo.type),
        )

        data_type = ExportTask.TASK_NAME_TO_DATA_TYPE_MAPPING.get(self.name)
        send_export_failed_info(export_file, data_type)

    def on_success(self, retval, task_id, args, kwargs):
        export_file_id = args[0]

        export_file = ExportFile.objects.get(pk=export_file_id)
        export_file.status = JobStatus.SUCCESS
        export_file.save(update_fields=["status", "updated_at"])
        events.export_success_event(
            export_file=export_file, user=export_file.user, app=export_file.app
        )


@app.task(name="export-products", base=ExportTask)
def export_products_task(
    export_file_id: int,
    scope: Dict[str, Union[str, dict]],
    export_info: Dict[str, list],
    file_type: str,
    delimiter: str = ",",
):
    export_file = ExportFile.objects.get(pk=export_file_id)
    export_products(export_file, scope, export_info, file_type, delimiter)


@app.task(name="export-gift-cards", base=ExportTask)
def export_gift_cards_task(
    export_file_id: int,
    scope: Dict[str, Union[str, dict]],
    file_type: str,
    delimiter: str = ",",
):
    export_file = ExportFile.objects.get(pk=export_file_id)
    export_gift_cards(export_file, scope, file_type, delimiter)
