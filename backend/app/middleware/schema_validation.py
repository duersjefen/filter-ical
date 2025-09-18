"""
Runtime Schema Validation Middleware for FastAPI
Validates all API responses against OpenAPI specification in real-time
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jsonschema import validate, ValidationError
from prance import ResolvingParser
import logging

logger = logging.getLogger(__name__)


class OpenAPISchemaValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates API responses against OpenAPI schema
    Only active in development/testing environments for performance
    """
    
    def __init__(self, app, enable_validation: bool = False):
        super().__init__(app)
        self.enable_validation = enable_validation
        self.openapi_spec = None
        self.schemas = {}
        
        if self.enable_validation:
            self._load_openapi_spec()
    
    def _load_openapi_spec(self):
        """Load and parse OpenAPI specification"""
        try:
            spec_path = Path(__file__).parent.parent.parent / "openapi.yaml"
            
            if spec_path.exists():
                # Parse and resolve the specification
                parser = ResolvingParser(str(spec_path))
                self.openapi_spec = parser.specification
                self.schemas = self.openapi_spec.get('components', {}).get('schemas', {})
                logger.info("✅ OpenAPI schema validation enabled")
            else:
                logger.warning("⚠️ OpenAPI specification not found - schema validation disabled")
                self.enable_validation = False
                
        except Exception as e:
            logger.error(f"❌ Failed to load OpenAPI spec: {e}")
            self.enable_validation = False
    
    def _match_path_pattern(self, actual_path: str, pattern_path: str) -> bool:
        """
        Match actual path against OpenAPI path pattern with parameters.
        E.g., "/api/calendar/cal_123/events" matches "/api/calendar/{calendar_id}/events"
        """
        actual_parts = actual_path.split('/')
        pattern_parts = pattern_path.split('/')
        
        if len(actual_parts) != len(pattern_parts):
            return False
            
        for actual, pattern in zip(actual_parts, pattern_parts):
            if pattern.startswith('{') and pattern.endswith('}'):
                # This is a path parameter, any value matches
                continue
            elif actual != pattern:
                # Literal path segment must match exactly
                return False
                
        return True
    
    def _get_endpoint_response_schema(self, path: str, method: str, status_code: int) -> Optional[Dict[str, Any]]:
        """Get the expected response schema for an endpoint"""
        if not self.openapi_spec:
            return None
            
        paths = self.openapi_spec.get('paths', {})
        
        # First try exact match
        endpoint_spec = paths.get(path)
        if not endpoint_spec:
            # Try pattern matching for paths with parameters
            for pattern_path, spec in paths.items():
                if self._match_path_pattern(path, pattern_path):
                    endpoint_spec = spec
                    break
        
        if not endpoint_spec:
            return None
            
        method_spec = endpoint_spec.get(method.lower(), {})
        responses = method_spec.get('responses', {})
        
        # Check for exact status code or default
        status_str = str(status_code)
        if status_str in responses:
            response_spec = responses[status_str]
        elif 'default' in responses:
            response_spec = responses['default']
        else:
            return None
            
        # Get JSON schema
        content = response_spec.get('content', {})
        json_content = content.get('application/json', {})
        return json_content.get('schema', {})
    
    def _resolve_schema_ref(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve $ref in schema to actual schema definition"""
        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path.startswith('#/components/schemas/'):
                schema_name = ref_path.split('/')[-1]
                return self.schemas.get(schema_name, schema)
        return schema
    
    def _validate_response_schema(self, data: Any, schema: Dict[str, Any], endpoint: str, method: str, status_code: int):
        """Validate response data against schema"""
        try:
            # Resolve any $ref references
            resolved_schema = self._resolve_schema_ref(schema)
            
            # Validate using jsonschema
            validate(instance=data, schema=resolved_schema)
            
        except ValidationError as e:
            error_msg = f"Schema validation failed for {method} {endpoint} (status {status_code}): {e.message}"
            logger.error(f"❌ {error_msg}")
            
            # In development, we want to know about schema violations immediately
            # In production, we would log but not fail the request
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Response data: {json.dumps(data, indent=2, default=str)}")
                logger.debug(f"Expected schema: {json.dumps(resolved_schema, indent=2)}")
            
        except Exception as e:
            logger.error(f"❌ Schema validation error for {method} {endpoint}: {e}")
    
    async def dispatch(self, request: Request, call_next):
        # Get the response
        response = await call_next(request)
        
        # Only validate if enabled and response is JSON
        if not self.enable_validation:
            return response
            
        # Skip validation for certain paths
        path = request.url.path
        if path.startswith('/docs') or path.startswith('/openapi') or path.startswith('/health'):
            return response
            
        # Only validate JSON responses
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            return response
            
        # Skip if no OpenAPI spec loaded
        if not self.openapi_spec:
            return response
            
        try:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
                
            # Parse JSON response
            if response_body:
                try:
                    response_data = json.loads(response_body.decode())
                except json.JSONDecodeError:
                    # Not valid JSON, skip validation
                    return Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                
                # Get expected schema for this endpoint
                method = request.method
                status_code = response.status_code
                
                # Try to match the path with OpenAPI paths (handle path parameters)
                schema = self._get_endpoint_response_schema(path, method, status_code)
                
                if schema:
                    # Validate the response
                    self._validate_response_schema(response_data, schema, path, method, status_code)
                else:
                    logger.debug(f"No schema found for {method} {path} (status {status_code})")
            
            # Return response with same content
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except Exception as e:
            logger.error(f"❌ Schema validation middleware error: {e}")
            # Return original response if validation fails
            return response


def create_validation_middleware(enable_validation: bool = False):
    """
    Factory function to create schema validation middleware
    
    Args:
        enable_validation: Whether to enable runtime validation
                          Should be True for development/testing, False for production
    """
    def middleware_factory(app):
        return OpenAPISchemaValidationMiddleware(app, enable_validation=enable_validation)
    
    return middleware_factory