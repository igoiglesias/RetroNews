from unittest.mock import patch, MagicMock

from services.scheduler import iniciar_scheduler


def test_iniciar_scheduler_retorna_scheduler():
    with patch("services.scheduler.os.getenv", return_value=None), \
         patch("services.scheduler.AsyncIOScheduler") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        resultado = iniciar_scheduler()

    assert resultado is mock_instance
    mock_instance.add_job.assert_called_once()
    mock_instance.start.assert_called_once()


def test_iniciar_scheduler_desativado():
    with patch.dict("os.environ", {"RETRONEWS_DISABLE_SCHEDULER": "1"}):
        resultado = iniciar_scheduler()

    assert resultado is None
