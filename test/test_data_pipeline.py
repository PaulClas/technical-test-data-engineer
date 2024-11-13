import pytest
from unittest.mock import patch, MagicMock, call
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
import requests
from prometheus_client import CollectorRegistry, Summary, Counter, Gauge
from moovitamix_fastapi.data_pipeline import fetch_data, save_data_to_db, retrieve_and_save_data, test_db_connection, tracks_table, users_table, listen_history_table

@pytest.fixture(autouse=True)
def reset_collector_registry():
    registry = CollectorRegistry()
    Summary._type = registry
    Counter._type = registry
    Gauge._type = registry

@patch('moovitamix_fastapi.data_pipeline.requests.get')
def test_fetch_data(mock_get):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"items": [{"id": 1, "name": "test"}]}
    mock_get.return_value = mock_response

    # Call the function
    result = fetch_data("tracks")

    # Assert the result
    assert result == {"items": [{"id": 1, "name": "test"}]}
    mock_get.assert_called_once_with("http://127.0.0.1:8000/tracks")

@patch('moovitamix_fastapi.data_pipeline.requests.get')
def test_fetch_data_error(mock_get):
    # Mock the API response to raise an exception
    mock_get.side_effect = requests.RequestException("API failure")

    # Call the function and assert it raises an exception
    with pytest.raises(requests.RequestException):
        fetch_data("tracks")

@patch('moovitamix_fastapi.data_pipeline.session')
def test_save_data_to_db(mock_session):
    # Mock the data and table
    data = {"items": [{"id": 1, "name": "test"}]}
    table = tracks_table

    # Call the function
    save_data_to_db(data, table)

    # Assert the database operations
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()

@patch('moovitamix_fastapi.data_pipeline.session')
def test_save_data_to_db_error(mock_session):
    # Mock the data and table
    data = {"items": [{"id": 1, "name": "test"}]}
    table = tracks_table

    # Mock the session to raise an exception
    mock_session.execute.side_effect = SQLAlchemyError("DB failure")

    # Call the function and assert it raises an exception
    with pytest.raises(SQLAlchemyError):
        save_data_to_db(data, table)

    # Assert the rollback is called
    mock_session.rollback.assert_called_once()

@patch('moovitamix_fastapi.data_pipeline.fetch_data')
@patch('moovitamix_fastapi.data_pipeline.save_data_to_db')
def test_retrieve_and_save_data(mock_save_data_to_db, mock_fetch_data):
    # Mock the fetch_data return values
    mock_fetch_data.side_effect = [
        {"items": [{"id": 2, "first_name": "user"}]},
        {"items": [{"id": 1, "name": "track"}]},
        {"items": [{"user_id": 1, "items": [1]}]}
    ]

    # Call the function
    retrieve_and_save_data()

    # Assert the fetch_data calls
    mock_fetch_data.assert_has_calls([
        call("users"),
        call("tracks"),
        call("listen_history")
    ])

    # Assert the save_data_to_db calls
    mock_save_data_to_db.assert_has_calls([
        call({"items": [{"id": 2, "first_name": "user"}]}, users_table),
        call({"items": [{"id": 1, "name": "track"}]}, tracks_table),
        call({"items": [{"user_id": 1, "items": [1]}]}, listen_history_table)
    ])


@patch('moovitamix_fastapi.data_pipeline.engine.connect')
def test_test_db_connection(mock_connect):
    # Mock the connection and execute method
    mock_connection = mock_connect.return_value.__enter__.return_value
    mock_connection.execute.return_value.fetchone.return_value = (1,)

    # Call the function
    test_db_connection()

    # Assert the database connection and query execution
    mock_connect.assert_called_once()
    assert mock_connection.execute.call_args[0][0].text == text("SELECT 1").text

@patch('moovitamix_fastapi.data_pipeline.engine.connect')
def test_test_db_connection_error(mock_connect):
    # Mock the connection to raise an exception
    mock_connect.side_effect = SQLAlchemyError("DB connection failure")

    # Call the function and assert it raises an exception
    with pytest.raises(SQLAlchemyError):
        test_db_connection()