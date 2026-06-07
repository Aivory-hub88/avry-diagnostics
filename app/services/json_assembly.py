"""
JSON assembly service for Blueprint structure construction.
"""

import uuid
from datetime import datetime
from typing import List

from app.models.blueprint import (
    AgentDefinition,
    WorkflowDefinition,
    IntegrationRequirement,
    BlueprintJSON
)


class JSONAssemblyService:
    """
    Assembles Blueprint components into structured JSON format.
    
    Generates:
    - Unique blueprint_id with "bp_" prefix
    - Version tracking
    - Schema version (aivory-v1)
    - Complete JSON structure
    """
    
    SCHEMA_VERSION = "aivory-v1"
    
    def assemble_blueprint_json(
        self,
        system_name: str,
        user_email: str,
        snapshot_id: str,
        agents: List[AgentDefinition],
        workflows: List[WorkflowDefinition],
        integrations: List[IntegrationRequirement],
        deployment_estimate: str,
        version: str = "1.0"
    ) -> dict:
        """
        Assemble all components into Blueprint JSON structure.
        
        Steps:
        1. Generate unique blueprint_id
        2. Set version (default "1.0" or provided)
        3. Add timestamp
        4. Structure agents with IDs
        5. Structure workflows
        6. Structure integrations
        7. Set schema_version to "aivory-v1"
        8. Validate against schema
        9. Return dict (will be serialized to JSON)
        
        Args:
            system_name: Generated system name
            user_email: User email address
            snapshot_id: Source snapshot ID
            agents: List of agent definitions
            workflows: List of workflow definitions
            integrations: List of integration requirements
            deployment_estimate: Time estimate string
            version: Blueprint version (default "1.0")
            
        Returns:
            Blueprint JSON as dict
        """
        # Generate unique blueprint_id
        blueprint_id = self._generate_blueprint_id()
        
        # Create Blueprint JSON structure
        blueprint_data = {
            "blueprint_id": blueprint_id,
            "version": version,
            "system_name": system_name,
            "generated_for": user_email,
            "generated_at": datetime.utcnow().isoformat(),
            "snapshot_id": snapshot_id,
            "agents": [agent.model_dump() for agent in agents],
            "workflows": [workflow.model_dump() for workflow in workflows],
            "integrations_required": [integration.model_dump() for integration in integrations],
            "deployment_estimate": deployment_estimate,
            "schema_version": self.SCHEMA_VERSION
        }
        
        # Validate against Pydantic model
        try:
            validated = BlueprintJSON(**blueprint_data)
            return validated.model_dump()
        except Exception as e:
            print(f"Blueprint JSON validation failed: {e}")
            # Return unvalidated data (will be caught by caller)
            return blueprint_data
    
    def _generate_blueprint_id(self) -> str:
        """
        Generate unique blueprint ID with "bp_" prefix.
        
        Returns:
            Blueprint ID (e.g., "bp_abc123def456")
        """
        unique_id = uuid.uuid4().hex[:12]
        return f"bp_{unique_id}"
    
    def validate_json_structure(self, blueprint_data: dict) -> bool:
        """
        Validate Blueprint JSON structure.
        
        Args:
            blueprint_data: Blueprint JSON dict
            
        Returns:
            True if valid
        """
        try:
            BlueprintJSON(**blueprint_data)
            return True
        except Exception as e:
            print(f"JSON validation error: {e}")
            return False
