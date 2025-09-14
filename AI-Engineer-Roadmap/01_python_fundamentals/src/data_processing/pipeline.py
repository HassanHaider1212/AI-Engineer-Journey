"""
Data Processing Pipeline

A robust, extensible data processing pipeline demonstrating:
- Object-oriented design
- Error handling
- Type hints
- Logging
- Configuration management
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
import csv
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcessingResult:
    """Result of a data processing operation."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DataValidator(ABC):
    """Abstract base class for data validators."""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate a single data record."""
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """Get error message for validation failure."""
        pass


class RequiredFieldValidator(DataValidator):
    """Validator for required fields."""
    
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields
        self._missing_fields: List[str] = []
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Check if all required fields are present."""
        self._missing_fields = [
            field for field in self.required_fields 
            if field not in data or data[field] is None
        ]
        return len(self._missing_fields) == 0
    
    def get_error_message(self) -> str:
        """Return error message for missing fields."""
        return f"Missing required fields: {', '.join(self._missing_fields)}"


class DataTransformer(ABC):
    """Abstract base class for data transformers."""
    
    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform a list of data records."""
        pass


class FieldMapper(DataTransformer):
    """Transform data by mapping field names."""
    
    def __init__(self, field_mapping: Dict[str, str]):
        self.field_mapping = field_mapping
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map field names according to the mapping dictionary."""
        transformed_data = []
        
        for record in data:
            transformed_record = {}
            for old_field, new_field in self.field_mapping.items():
                if old_field in record:
                    transformed_record[new_field] = record[old_field]
                else:
                    # Keep original field if mapping doesn't exist
                    transformed_record[old_field] = record[old_field]
            transformed_data.append(transformed_record)
        
        return transformed_data


class DataProcessor:
    """Main data processing pipeline class."""
    
    def __init__(self, name: str = "DataProcessor"):
        self.name = name
        self.validators: List[DataValidator] = []
        self.transformers: List[DataTransformer] = []
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the processor."""
        logger = logging.getLogger(f"{self.name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def add_validator(self, validator: DataValidator) -> None:
        """Add a validator to the pipeline."""
        self.validators.append(validator)
        self.logger.info(f"Added validator: {validator.__class__.__name__}")
    
    def add_transformer(self, transformer: DataTransformer) -> None:
        """Add a transformer to the pipeline."""
        self.transformers.append(transformer)
        self.logger.info(f"Added transformer: {transformer.__class__.__name__}")
    
    def validate_data(self, data: List[Dict[str, Any]]) -> ProcessingResult:
        """Validate all data records."""
        errors = []
        valid_data = []
        
        for i, record in enumerate(data):
            record_valid = True
            for validator in self.validators:
                if not validator.validate(record):
                    errors.append(f"Record {i}: {validator.get_error_message()}")
                    record_valid = False
                    break
            
            if record_valid:
                valid_data.append(record)
        
        success = len(errors) == 0
        return ProcessingResult(
            success=success,
            data=valid_data if success else None,
            errors=errors if not success else None,
            metadata={"total_records": len(data), "valid_records": len(valid_data)}
        )
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all transformers to the data."""
        transformed_data = data
        
        for transformer in self.transformers:
            self.logger.info(f"Applying transformer: {transformer.__class__.__name__}")
            transformed_data = transformer.transform(transformed_data)
        
        return transformed_data
    
    def process(self, data: List[Dict[str, Any]]) -> ProcessingResult:
        """Run the complete processing pipeline."""
        self.logger.info(f"Starting processing of {len(data)} records")
        
        # Validate data
        validation_result = self.validate_data(data)
        if not validation_result.success:
            self.logger.error(f"Validation failed: {validation_result.errors}")
            return validation_result
        
        # Transform data
        try:
            transformed_data = self.transform_data(validation_result.data)
            self.logger.info(f"Successfully processed {len(transformed_data)} records")
            
            return ProcessingResult(
                success=True,
                data=transformed_data,
                metadata={
                    "processed_at": datetime.now().isoformat(),
                    "total_records": len(data),
                    "processed_records": len(transformed_data)
                }
            )
        
        except Exception as e:
            error_msg = f"Transformation failed: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                errors=[error_msg]
            )


class DataReader:
    """Utility class for reading data from various sources."""
    
    @staticmethod
    def read_json(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Read data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]
        
        return data
    
    @staticmethod
    def read_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Read data from CSV file."""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        return data


class DataWriter:
    """Utility class for writing data to various formats."""
    
    @staticmethod
    def write_json(data: List[Dict[str, Any]], file_path: Union[str, Path]) -> None:
        """Write data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def write_csv(data: List[Dict[str, Any]], file_path: Union[str, Path]) -> None:
        """Write data to CSV file."""
        if not data:
            return
        
        fieldnames = data[0].keys()
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)


# Example usage and demonstration
if __name__ == "__main__":
    # Sample data
    sample_data = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"},  # Missing age
        {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "age": 35},
    ]
    
    # Create processor
    processor = DataProcessor("SampleProcessor")
    
    # Add validators
    processor.add_validator(RequiredFieldValidator(["id", "name", "email", "age"]))
    
    # Add transformers
    field_mapping = {"id": "user_id", "name": "full_name"}
    processor.add_transformer(FieldMapper(field_mapping))
    
    # Process data
    result = processor.process(sample_data)
    
    if result.success:
        print(f"Processing successful! Processed {len(result.data)} records")
        print("Sample processed record:", result.data[0])
    else:
        print("Processing failed!")
        for error in result.errors:
            print(f"Error: {error}")
