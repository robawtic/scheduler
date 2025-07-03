import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

def test_database_error_generic_message(client, db_session, csrf_token):
    """
    Test that database errors return a generic message without exposing details.
    """
    # Mock the SQLAlchemy session to raise an exception
    with patch('sqlalchemy.orm.Session.query', side_effect=SQLAlchemyError("Sensitive database error details")):
        # Try to access an endpoint that uses the database
        response = client.get("/api/v1/schedules")
        
        # Check that the response has a 500 status code
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Check that the error message is generic
        data = response.json()
        assert "message" in data
        assert "An internal database error occurred" in data["message"]
        
        # Check that no error details are exposed
        assert "details" in data
        assert data["details"] is None
        
        # Ensure the sensitive error message is not in the response
        assert "Sensitive database error details" not in str(response.content)

def test_unhandled_exception_generic_message(client, db_session, csrf_token):
    """
    Test that unhandled exceptions return a generic message without exposing details.
    """
    # Mock the schedule service to raise an exception
    with patch('domain.services.schedule_service.ScheduleService.generate_schedule', 
               side_effect=Exception("Sensitive internal error details")):
        # Try to create a schedule
        response = client.post(
            "/api/v1/schedules",
            json={
                "team_id": 1,
                "start_date": "2023-01-01T00:00:00Z",
                "periods_per_day": 4
            },
            headers={"X-CSRF-Token": csrf_token}
        )
        
        # Check that the response has a 400 status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the error message is generic
        data = response.json()
        assert "detail" in data
        assert "Failed to create schedule" in data["detail"]
        
        # Ensure the sensitive error message is not in the response
        assert "Sensitive internal error details" not in str(response.content)

def test_validation_error_descriptive_message(client, db_session, csrf_token):
    """
    Test that validation errors return descriptive messages to help users.
    """
    # Try to register with invalid data
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "ab",  # Too short
            "email": "invalid-email",
            "password": "short",
            "confirm_password": "different"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the response has a 422 status code
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check that the error details are descriptive
    data = response.json()
    assert "detail" in data
    
    # Check that validation errors for each field are included
    validation_errors = data["detail"]
    assert any("username" in error["loc"] for error in validation_errors)
    assert any("email" in error["loc"] for error in validation_errors)
    assert any("password" in error["loc"] for error in validation_errors)
    assert any("confirm_password" in error["loc"] for error in validation_errors)