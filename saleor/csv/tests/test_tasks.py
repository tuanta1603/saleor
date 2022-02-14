import datetime
from unittest.mock import ANY, Mock, patch

import pytz
from freezegun import freeze_time

from ...core import JobStatus
from .. import ExportEvents, FileTypes
from ..models import ExportEvent
from ..tasks import ExportTask, export_gift_cards_task, export_products_task


@patch("saleor.csv.tasks.export_products")
def test_export_products_task(export_products_mock, user_export_file):
    # given
    scope = {"all": ""}
    export_info = {"fields": "name"}
    file_type = FileTypes.CSV
    delimiter = ";"

    # when
    export_products_task(user_export_file.id, scope, export_info, file_type, delimiter)

    # then
    export_products_mock.assert_called_once_with(
        user_export_file, scope, export_info, file_type, delimiter
    )


@patch("saleor.csv.tasks.send_export_failed_info")
@patch("saleor.csv.tasks.export_products")
def test_export_products_task_failed(
    export_products_mock, send_export_failed_info_mock, user_export_file
):
    # given
    scope = {"all": ""}
    export_info = {"fields": "name"}
    file_type = FileTypes.CSV
    delimiter = ";"

    exc_message = "Test error"
    export_products_mock.side_effect = Exception(exc_message)

    # when
    export_products_task.delay(
        user_export_file.id, scope, export_info, file_type, delimiter
    )

    # then
    send_export_failed_info_mock.assert_called_once_with(user_export_file, "products")


@patch("saleor.csv.tasks.export_gift_cards")
def test_export_gift_cards_task(export_gift_cards_mock, user_export_file):
    # given
    scope = {"all": ""}
    file_type = FileTypes.CSV
    delimiter = ";"

    # when
    export_gift_cards_task(user_export_file.id, scope, file_type, delimiter)

    # then
    export_gift_cards_mock.assert_called_once_with(
        user_export_file, scope, file_type, delimiter
    )


@patch("saleor.csv.tasks.send_export_failed_info")
@patch("saleor.csv.tasks.export_gift_cards")
def test_export_gift_cards_task_failed(
    export_gift_cards_mock, send_export_failed_info_mock, user_export_file
):
    # given
    scope = {"all": ""}
    file_type = FileTypes.CSV
    delimiter = ";"

    exc_message = "Test error"
    export_gift_cards_mock.side_effect = Exception(exc_message)

    # when
    export_gift_cards_task.delay(user_export_file.id, scope, file_type, delimiter)

    # then
    send_export_failed_info_mock.assert_called_once_with(user_export_file, "gift cards")


@patch("saleor.csv.tasks.send_export_failed_info")
def test_on_task_failure(send_export_failed_info_mock, user_export_file):
    # given
    exc = Exception("Test")
    task_id = "task_id"
    args = [user_export_file.pk, {"all": ""}]
    kwargs = {}
    info_type = "Test error"
    info = Mock(type=info_type)

    assert user_export_file.status == JobStatus.PENDING
    assert user_export_file.created_at
    previous_updated_at = user_export_file.updated_at

    with freeze_time(datetime.datetime.now()) as frozen_datetime:
        # when
        ExportTask().on_failure(exc, task_id, args, kwargs, info)

        # then
        user_export_file.refresh_from_db()
        assert user_export_file.updated_at == pytz.utc.localize(frozen_datetime())

    assert user_export_file.updated_at != previous_updated_at
    assert user_export_file.status == JobStatus.FAILED
    assert user_export_file.created_at
    assert user_export_file.updated_at != previous_updated_at
    export_failed_event = ExportEvent.objects.get(
        export_file=user_export_file,
        user=user_export_file.user,
        app=None,
        type=ExportEvents.EXPORT_FAILED,
    )
    assert export_failed_event.parameters == {
        "message": str(exc),
        "error_type": info_type,
    }

    send_export_failed_info_mock.assert_called_once_with(user_export_file, ANY)


@patch("saleor.csv.tasks.send_export_failed_info")
def test_on_task_failure_for_app(send_export_failed_info_mock, app_export_file):
    # given
    exc = Exception("Test")
    task_id = "task_id"
    args = [app_export_file.pk, {"all": ""}]
    kwargs = {}
    info_type = "Test error"
    info = Mock(type=info_type)

    assert app_export_file.status == JobStatus.PENDING
    assert app_export_file.created_at
    previous_updated_at = app_export_file.updated_at

    with freeze_time(datetime.datetime.now()) as frozen_datetime:
        # when
        ExportTask().on_failure(exc, task_id, args, kwargs, info)

        # then
        app_export_file.refresh_from_db()
        assert app_export_file.updated_at == pytz.utc.localize(frozen_datetime())

    assert app_export_file.updated_at != previous_updated_at
    assert app_export_file.status == JobStatus.FAILED
    assert app_export_file.created_at
    assert app_export_file.updated_at != previous_updated_at
    export_failed_event = ExportEvent.objects.get(
        export_file=app_export_file,
        user=None,
        app=app_export_file.app,
        type=ExportEvents.EXPORT_FAILED,
    )
    assert export_failed_event.parameters == {
        "message": str(exc),
        "error_type": info_type,
    }

    send_export_failed_info_mock.called_once_with(app_export_file, ANY)


def test_on_task_success(user_export_file):
    # given
    task_id = "task_id"
    args = [user_export_file.pk, {"filter": {}}]
    kwargs = {}

    assert user_export_file.status == JobStatus.PENDING
    assert user_export_file.created_at
    previous_updated_at = user_export_file.updated_at

    with freeze_time(datetime.datetime.now()) as frozen_datetime:
        # when
        ExportTask().on_success(None, task_id, args, kwargs)

        # then
        user_export_file.refresh_from_db()
        assert user_export_file.updated_at == pytz.utc.localize(frozen_datetime())
        assert user_export_file.updated_at != previous_updated_at

    assert user_export_file.status == JobStatus.SUCCESS
    assert user_export_file.created_at
    assert ExportEvent.objects.filter(
        export_file=user_export_file,
        user=user_export_file.user,
        type=ExportEvents.EXPORT_SUCCESS,
    )
