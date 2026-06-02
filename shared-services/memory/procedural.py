"""Procedural Memory — versioned system prompts, instructions, and workflows.

Procedural memory stores the explicit instructions (system prompts, standard
operating procedures, workflow steps) that guide agent behavior. It allows
prompts to be versioned, tested, and updated independently of code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class PromptTemplate(BaseModel):
    """A versioned system prompt or instruction template."""

    name: str
    version: str
    system_prompt: str
    examples: list[dict[str, str]] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    description: str = ""
    author: str = "system"


class ProceduralMemory:
    """Manages versioned prompts, SOPs, and workflow instructions.

    Prompts are loaded from disk (e.g. JSON/YAML files in a prompts directory)
    but could be extended to fetch from a database for dynamic updates.

    Usage:
        ```python
        memory = ProceduralMemory(prompts_dir="./prompts")
        
        # Load a prompt template
        template = memory.get_prompt("healthcare/nabh_gap_analysis", version="v1.0")
        
        # Format the system prompt with inputs
        system_message = memory.format_prompt(
            template.name, 
            inputs={"client_name": "Apollo", "tier": "premium"}
        )
        ```
    """

    def __init__(self, prompts_dir: str | Path | None = None) -> None:
        self._prompts_dir = Path(prompts_dir) if prompts_dir else None
        self._templates: dict[str, dict[str, PromptTemplate]] = {}
        self._log = logger.bind(component="procedural_memory")

        if self._prompts_dir and self._prompts_dir.exists():
            self._load_all_prompts()

    def register_prompt(self, template: PromptTemplate) -> None:
        """Register a prompt template in memory."""
        if template.name not in self._templates:
            self._templates[template.name] = {}
        self._templates[template.name][template.version] = template
        self._log.debug(
            "prompt_registered",
            name=template.name,
            version=template.version,
        )

    def get_prompt(
        self,
        name: str,
        version: str | None = None,
    ) -> PromptTemplate:
        """Retrieve a prompt template by name and optional version.

        If version is None, returns the most recently registered version
        (alphabetical sort on version string).

        Raises:
            KeyError: If the prompt name or version is not found.
        """
        if name not in self._templates:
            raise KeyError(f"Prompt template '{name}' not found.")

        versions = self._templates[name]

        if version is not None:
            if version not in versions:
                raise KeyError(f"Version '{version}' for prompt '{name}' not found.")
            return versions[version]

        # Default to latest version (simple string sort, assumes semantic versioning like v1.0, v1.1)
        latest_version = sorted(versions.keys())[-1]
        return versions[latest_version]

    def format_prompt(
        self,
        name: str,
        inputs: dict[str, Any],
        version: str | None = None,
    ) -> str:
        """Retrieve and format a system prompt with the given inputs.

        Args:
            name: The name of the prompt template.
            inputs: Dictionary of template variables to substitute.
            version: Optional specific version to use.

        Returns:
            The formatted system prompt string.

        Raises:
            ValueError: If required inputs are missing.
        """
        template = self.get_prompt(name, version)

        # Validate required inputs
        missing = [req for req in template.required_inputs if req not in inputs]
        if missing:
            raise ValueError(
                f"Missing required inputs for prompt '{name}': {missing}"
            )

        try:
            # Simple string formatting (.format)
            # In a real system, you might use Jinja2 for complex logic
            formatted = template.system_prompt.format(**inputs)
            return formatted
        except KeyError as e:
            raise ValueError(
                f"Input missing for placeholder in template '{name}': {e!s}"
            )

    def _load_all_prompts(self) -> None:
        """Load all JSON prompt files from the prompts directory."""
        if not self._prompts_dir:
            return

        count = 0
        for path in self._prompts_dir.rglob("*.json"):
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    template = PromptTemplate.model_validate(data)
                    self.register_prompt(template)
                    count += 1
            except Exception as e:
                self._log.error(
                    "failed_to_load_prompt_file",
                    file=str(path),
                    error=str(e),
                )

        if count > 0:
            self._log.info("loaded_prompts_from_disk", count=count, dir=str(self._prompts_dir))

    @property
    def registered_prompts(self) -> list[str]:
        """List all registered prompt names."""
        return list(self._templates.keys())
