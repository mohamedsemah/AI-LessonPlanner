"""
Base Agent Class for Multi-Agent Lesson Planning System

This module provides the foundational BaseAgent class that all specialized agents inherit from.
It includes common functionality for AI interactions, error handling, logging, and result processing.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
import json
import os

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent lesson planning system.
    
    Provides common functionality including:
    - OpenAI client management
    - Error handling and retry logic
    - Logging and monitoring
    - Result validation and processing
    - Common AI interaction patterns
    """
    
    def __init__(self, client: Optional[AsyncOpenAI] = None):
        """
        Initialize the base agent.
        
        Args:
            client: Optional OpenAI client. If not provided, creates a new one.
        """
        self.client = client or self._create_openai_client()
        self.agent_name = self.__class__.__name__
        self.logger = logging.getLogger(f"agents.{self.agent_name}")
        
    def _create_openai_client(self) -> AsyncOpenAI:
        """Create and configure OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return AsyncOpenAI(api_key=api_key)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        This method must be implemented by all concrete agent classes.
        
        Args:
            input_data: Dictionary containing input data for processing
            
        Returns:
            Dictionary containing the processed results
            
        Raises:
            NotImplementedError: If not implemented by concrete class
        """
        raise NotImplementedError("Subclasses must implement the process method")
    
    async def _call_openai(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        max_retries: int = 3
    ) -> str:
        """
        Make a call to OpenAI with retry logic and error handling.
        
        Args:
            messages: List of message dictionaries for the chat completion
            model: OpenAI model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated text content
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"OpenAI call attempt {attempt + 1}/{max_retries}")
                
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from OpenAI")
                
                self.logger.debug(f"OpenAI call successful on attempt {attempt + 1}")
                return content.strip()
                
            except Exception as e:
                self.logger.warning(f"OpenAI call attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == max_retries - 1:
                    self.logger.error(f"All OpenAI call attempts failed: {str(e)}")
                    raise
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
    
    def _clean_json_response(self, content: str) -> str:
        """
        Clean and extract JSON from OpenAI response.
        
        Args:
            content: Raw content from OpenAI
            
        Returns:
            Cleaned JSON string
        """
        if not content:
            return ""
        
        # Remove markdown code blocks
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[4:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
    
    def _parse_json_response(self, content: str, expected_type: str = "object") -> Any:
        """
        Parse JSON response with error handling.
        
        Args:
            content: JSON string to parse
            expected_type: Expected type ("object", "array", "string")
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            cleaned_content = self._clean_json_response(content)
            parsed_data = json.loads(cleaned_content)
            
            # Validate expected type
            if expected_type == "array" and not isinstance(parsed_data, list):
                raise ValueError("Expected array but got object")
            elif expected_type == "object" and not isinstance(parsed_data, dict):
                raise ValueError("Expected object but got array")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed: {str(e)}")
            self.logger.error(f"Content: {content[:500]}...")
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing JSON: {str(e)}")
            raise
    
    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present in data.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ValueError: If any required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    def _log_processing_start(self, input_summary: str) -> None:
        """Log the start of processing."""
        self.logger.info(f"Starting {self.agent_name} processing: {input_summary}")
    
    def _log_processing_success(self, output_summary: str) -> None:
        """Log successful processing completion."""
        self.logger.info(f"{self.agent_name} processing completed successfully: {output_summary}")
    
    def _log_processing_error(self, error: Exception) -> None:
        """Log processing error."""
        self.logger.error(f"{self.agent_name} processing failed: {str(error)}")
    
    def _create_error_response(self, error: Exception, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create standardized error response.
        
        Args:
            error: Exception that occurred
            fallback_data: Optional fallback data to return
            
        Returns:
            Error response dictionary
        """
        error_response = {
            "success": False,
            "error": str(error),
            "agent": self.agent_name,
            "fallback_used": fallback_data is not None
        }
        
        if fallback_data:
            error_response["data"] = fallback_data
        
        return error_response
    
    def _create_success_response(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create standardized success response.
        
        Args:
            data: Processed data
            metadata: Optional metadata about processing
            
        Returns:
            Success response dictionary
        """
        response = {
            "success": True,
            "data": data,
            "agent": self.agent_name
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    async def _execute_with_fallback(
        self, 
        main_process: callable, 
        fallback_process: callable,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute main process with fallback on failure.
        
        Args:
            main_process: Main processing function
            fallback_process: Fallback processing function
            input_data: Input data for processing
            
        Returns:
            Processing result dictionary
        """
        try:
            self.logger.info(f"Executing main process in {self.agent_name}")
            result = await main_process(input_data)
            return self._create_success_response(result)
            
        except Exception as e:
            self.logger.warning(f"Main process failed in {self.agent_name}, trying fallback: {str(e)}")
            
            try:
                fallback_result = await fallback_process(input_data)
                return self._create_success_response(fallback_result, {"fallback_used": True})
                
            except Exception as fallback_error:
                self.logger.error(f"Both main and fallback processes failed in {self.agent_name}: {str(fallback_error)}")
                return self._create_error_response(fallback_error)
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.agent_name}(client={'configured' if self.client else 'none'})"
