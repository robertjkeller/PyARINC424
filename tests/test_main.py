from unittest.mock import MagicMock, patch


def test_main_success():
    dummy_config = MagicMock(name="dummy_config")
    dummy_config.file_loc = "dummy_location"

    dummy_db = MagicMock(name="dummy_db")
    dummy_context = MagicMock(name="dummy_context")
    dummy_db.connect.return_value = dummy_context
    dummy_context.__enter__.return_value = None
    dummy_context.__exit__.return_value = None

    dummy_parser = MagicMock(name="dummy_parser")

    with (
        patch("main.UserConfigs", return_value=dummy_config) as mock_configs,
        patch("main.get_db", return_value=dummy_db) as mock_get_db,
        patch("main.ArincParser", return_value=dummy_parser) as mock_parser_class,
    ):

        import main  # type: ignore

        main.main()

        mock_configs.assert_called_once()

        mock_get_db.assert_called_once_with(dummy_config)

        dummy_db.connect.assert_called_once()
        dummy_context.__enter__.assert_called_once()
        dummy_context.__exit__.assert_called_once()

        mock_parser_class.assert_called_once_with(dummy_db, dummy_config.file_loc)

        dummy_parser.parse.assert_called_once()
