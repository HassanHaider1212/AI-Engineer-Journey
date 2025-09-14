"""
Tests for the data processing pipeline.

This module demonstrates comprehensive testing practices including:
- Unit tests for individual components
- Integration tests for the complete pipeline
- Mocking external dependencies
- Test fixtures and parametrization
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from typing import List, Dict, Any

from src.data_processing.pipeline import (
    DataProcessor, RequiredFieldValidator, FieldMapper,
    ProcessingResult, DataReader, DataWriter
)


class TestRequiredFieldValidator:
    """Test cases for RequiredFieldValidator."""
    
    def test_validate_success(self):
        """Test successful validation with all required fields."""
        validator = RequiredFieldValidator(["id", "name", "email"])
        data = {"id": 1, "name": "John", "email": "john@example.com"}
        
        assert validator.validate(data) is True
        assert validator.get_error_message() == "Missing required fields: "
    
    def test_validate_missing_fields(self):
        """Test validation failure with missing fields."""
        validator = RequiredFieldValidator(["id", "name", "email"])
        data = {"id": 1, "name": "John"}  # Missing email
        
        assert validator.validate(data) is False
        assert "email" in validator.get_error_message()
    
    def test_validate_none_values(self):
        """Test validation with None values."""
        validator = RequiredFieldValidator(["id", "name"])
        data = {"id": 1, "name": None}
        
        assert validator.validate(data) is False
        assert "name" in validator.get_error_message()
    
    def test_validate_empty_required_fields(self):
        """Test validator with no required fields."""
        validator = RequiredFieldValidator([])
        data = {"id": 1, "name": "John"}
        
        assert validator.validate(data) is True


class TestFieldMapper:
    """Test cases for FieldMapper transformer."""
    
    def test_transform_success(self):
        """Test successful field mapping."""
        mapper = FieldMapper({"id": "user_id", "name": "full_name"})
        data = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"}
        ]
        
        result = mapper.transform(data)
        
        assert len(result) == 2
        assert "user_id" in result[0]
        assert "full_name" in result[0]
        assert "email" in result[0]  # Unmapped field should remain
        assert result[0]["user_id"] == 1
        assert result[0]["full_name"] == "John"
    
    def test_transform_partial_mapping(self):
        """Test mapping with only some fields present."""
        mapper = FieldMapper({"id": "user_id", "missing": "new_field"})
        data = [{"id": 1, "name": "John"}]
        
        result = mapper.transform(data)
        
        assert "user_id" in result[0]
        assert "name" in result[0]  # Original field remains
        assert "missing" not in result[0]  # Missing field not added
        assert result[0]["user_id"] == 1
    
    def test_transform_empty_data(self):
        """Test transformation with empty data."""
        mapper = FieldMapper({"id": "user_id"})
        data = []
        
        result = mapper.transform(data)
        
        assert result == []


class TestDataProcessor:
    """Test cases for DataProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a DataProcessor instance for testing."""
        return DataProcessor("TestProcessor")
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return [
            {"id": 1, "name": "John", "email": "john@example.com", "age": 30},
            {"id": 2, "name": "Jane", "email": "jane@example.com", "age": 25},
            {"id": 3, "name": "Bob", "email": "bob@example.com"},  # Missing age
        ]
    
    def test_add_validator(self, processor):
        """Test adding validators to the processor."""
        validator = RequiredFieldValidator(["id", "name"])
        processor.add_validator(validator)
        
        assert len(processor.validators) == 1
        assert processor.validators[0] == validator
    
    def test_add_transformer(self, processor):
        """Test adding transformers to the processor."""
        transformer = FieldMapper({"id": "user_id"})
        processor.add_transformer(transformer)
        
        assert len(processor.transformers) == 1
        assert processor.transformers[0] == transformer
    
    def test_validate_data_success(self, processor, sample_data):
        """Test successful data validation."""
        validator = RequiredFieldValidator(["id", "name", "email"])
        processor.add_validator(validator)
        
        result = processor.validate_data(sample_data)
        
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 3
        assert result.errors is None
    
    def test_validate_data_failure(self, processor, sample_data):
        """Test data validation failure."""
        validator = RequiredFieldValidator(["id", "name", "email", "age"])
        processor.add_validator(validator)
        
        result = processor.validate_data(sample_data)
        
        assert result.success is False
        assert result.data is None
        assert result.errors is not None
        assert len(result.errors) == 1  # One record missing age
    
    def test_transform_data(self, processor, sample_data):
        """Test data transformation."""
        transformer = FieldMapper({"id": "user_id", "name": "full_name"})
        processor.add_transformer(transformer)
        
        result = processor.transform_data(sample_data)
        
        assert len(result) == 3
        assert "user_id" in result[0]
        assert "full_name" in result[0]
        assert result[0]["user_id"] == 1
    
    def test_process_success(self, processor, sample_data):
        """Test successful complete processing."""
        # Add validator that will pass
        validator = RequiredFieldValidator(["id", "name", "email"])
        processor.add_validator(validator)
        
        # Add transformer
        transformer = FieldMapper({"id": "user_id"})
        processor.add_transformer(transformer)
        
        result = processor.process(sample_data)
        
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 3
        assert "user_id" in result.data[0]
        assert result.metadata is not None
        assert "processed_at" in result.metadata
    
    def test_process_validation_failure(self, processor, sample_data):
        """Test processing with validation failure."""
        # Add validator that will fail
        validator = RequiredFieldValidator(["id", "name", "email", "age"])
        processor.add_validator(validator)
        
        result = processor.process(sample_data)
        
        assert result.success is False
        assert result.data is None
        assert result.errors is not None
    
    def test_process_transformation_error(self, processor, sample_data):
        """Test processing with transformation error."""
        # Add validator that will pass
        validator = RequiredFieldValidator(["id", "name", "email"])
        processor.add_validator(validator)
        
        # Add transformer that will raise an exception
        mock_transformer = Mock()
        mock_transformer.transform.side_effect = Exception("Transformation error")
        processor.add_transformer(mock_transformer)
        
        result = processor.process(sample_data)
        
        assert result.success is False
        assert result.errors is not None
        assert "Transformation error" in result.errors[0]


class TestDataReader:
    """Test cases for DataReader utility class."""
    
    def test_read_json_success(self):
        """Test successful JSON reading."""
        json_data = '[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]'
        
        with patch("builtins.open", mock_open(read_data=json_data)):
            result = DataReader.read_json("test.json")
            
            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[0]["name"] == "John"
    
    def test_read_json_single_object(self):
        """Test reading JSON with single object."""
        json_data = '{"id": 1, "name": "John"}'
        
        with patch("builtins.open", mock_open(read_data=json_data)):
            result = DataReader.read_json("test.json")
            
            assert len(result) == 1
            assert result[0]["id"] == 1
    
    def test_read_csv_success(self):
        """Test successful CSV reading."""
        csv_data = "id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com"
        
        with patch("builtins.open", mock_open(read_data=csv_data)):
            result = DataReader.read_csv("test.csv")
            
            assert len(result) == 2
            assert result[0]["id"] == "1"
            assert result[0]["name"] == "John"
            assert result[0]["email"] == "john@example.com"


class TestDataWriter:
    """Test cases for DataWriter utility class."""
    
    def test_write_json_success(self):
        """Test successful JSON writing."""
        data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        
        with patch("builtins.open", mock_open()) as mock_file:
            DataWriter.write_json(data, "output.json")
            
            mock_file.assert_called_once_with("output.json", 'w', encoding='utf-8')
    
    def test_write_csv_success(self):
        """Test successful CSV writing."""
        data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        
        with patch("builtins.open", mock_open()) as mock_file:
            DataWriter.write_csv(data, "output.csv")
            
            mock_file.assert_called_once_with("output.csv", 'w', newline='', encoding='utf-8')
    
    def test_write_csv_empty_data(self):
        """Test CSV writing with empty data."""
        data = []
        
        with patch("builtins.open", mock_open()) as mock_file:
            DataWriter.write_csv(data, "output.csv")
            
            # Should not call open for empty data
            mock_file.assert_not_called()


class TestProcessingResult:
    """Test cases for ProcessingResult dataclass."""
    
    def test_success_result(self):
        """Test successful processing result."""
        data = [{"id": 1, "name": "John"}]
        metadata = {"processed_at": "2024-01-01"}
        
        result = ProcessingResult(
            success=True,
            data=data,
            metadata=metadata
        )
        
        assert result.success is True
        assert result.data == data
        assert result.errors is None
        assert result.metadata == metadata
    
    def test_failure_result(self):
        """Test failed processing result."""
        errors = ["Validation failed", "Missing field"]
        
        result = ProcessingResult(
            success=False,
            errors=errors
        )
        
        assert result.success is False
        assert result.data is None
        assert result.errors == errors
        assert result.metadata is None


# Integration test
class TestDataProcessingIntegration:
    """Integration tests for the complete data processing pipeline."""
    
    def test_complete_pipeline(self):
        """Test the complete pipeline with real-world scenario."""
        # Sample data with some issues
        data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"},  # Missing age
            {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "age": 35},
        ]
        
        # Create processor
        processor = DataProcessor("IntegrationTest")
        
        # Add validators
        processor.add_validator(RequiredFieldValidator(["id", "name", "email", "age"]))
        
        # Add transformers
        processor.add_transformer(FieldMapper({
            "id": "user_id",
            "name": "full_name",
            "email": "email_address"
        }))
        
        # Process data
        result = processor.process(data)
        
        # Verify results
        assert result.success is False  # Should fail due to missing age in one record
        assert result.errors is not None
        assert len(result.errors) == 1
        
        # Test with valid data
        valid_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
        ]
        
        result = processor.process(valid_data)
        
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 2
        assert "user_id" in result.data[0]
        assert "full_name" in result.data[0]
        assert "email_address" in result.data[0]
