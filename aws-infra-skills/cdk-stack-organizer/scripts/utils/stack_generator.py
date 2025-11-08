"""
Stack Generator Utility

Generates TypeScript CDK stack files from organized constructs.
"""

from typing import Dict, List, Any
from pathlib import Path


class StackGenerator:
    """Generate CDK stack TypeScript files"""

    def __init__(self, cdk_version: str = "2.0.0", stack_prefix: str = ""):
        self.cdk_version = cdk_version
        self.stack_prefix = stack_prefix

    def generate_stack(
        self, stack_name: str, constructs: List[Dict[str, Any]], stack_plan
    ) -> str:
        """
        Generate a complete stack TypeScript file

        Args:
            stack_name: Name of the stack
            constructs: List of construct information
            stack_plan: The complete stack plan (for cross-stack refs)

        Returns:
            TypeScript code for the stack
        """
        # Apply stack prefix if provided
        full_stack_name = f"{self.stack_prefix}{stack_name}" if self.stack_prefix else stack_name

        # Generate imports
        imports = self._generate_imports(constructs, stack_plan, stack_name)

        # Generate stack class
        stack_class = self._generate_stack_class(
            full_stack_name, constructs, stack_plan, stack_name
        )

        # Combine into complete file
        return f"{imports}\n\n{stack_class}"

    def _generate_imports(
        self, constructs: List[Dict[str, Any]], stack_plan, stack_name: str
    ) -> str:
        """Generate import statements"""
        imports = [
            "import * as cdk from 'aws-cdk-lib';",
            "import { Construct } from 'constructs';",
        ]

        # Import AWS modules based on resource types
        aws_modules = set()
        for construct in constructs:
            resource_type = construct["type"]
            if resource_type == "lambdas":
                aws_modules.add("lambda")
                aws_modules.add("iam")  # Lambda needs IAM
            elif resource_type == "dynamodb":
                aws_modules.add("dynamodb")
            elif resource_type == "iam":
                aws_modules.add("iam")
            elif resource_type == "s3":
                aws_modules.add("s3")
            elif resource_type == "eventbridge":
                aws_modules.add("events")

        for module in sorted(aws_modules):
            imports.append(f"import * as {module} from 'aws-cdk-lib/aws-{module}';")

        # Add blank line
        imports.append("")

        # Import construct classes
        # Group by resource type for cleaner imports
        constructs_by_type = {}
        for construct in constructs:
            resource_type = construct["type"]
            if resource_type not in constructs_by_type:
                constructs_by_type[resource_type] = []
            constructs_by_type[resource_type].append(construct)

        # Generate relative imports for each type
        for resource_type, type_constructs in constructs_by_type.items():
            imports.append(f"// {resource_type.capitalize()} constructs")
            for construct in type_constructs:
                class_name = construct["class_name"]
                file_name = construct["file_path"].stem
                # Import from the original generated constructs
                # We'll copy these files to the lib/ directory or reference them
                imports.append(
                    f"// import {{ {class_name} }} from '../constructs/{resource_type}/{file_name}';"
                )
                imports.append(
                    f"// TODO: Copy construct files or adjust import path"
                )

        return "\n".join(imports)

    def _generate_stack_class(
        self,
        stack_name: str,
        constructs: List[Dict[str, Any]],
        stack_plan,
        original_stack_name: str,
    ) -> str:
        """Generate the stack class definition"""
        lines = []

        # Stack interface for props
        dependencies = stack_plan.dependencies.get(original_stack_name, [])
        if dependencies:
            lines.append(f"export interface {stack_name}Props extends cdk.StackProps {{")
            for dep_stack in dependencies:
                # Add references to dependent stacks
                dep_stack_name = (
                    f"{self.stack_prefix}{dep_stack}" if self.stack_prefix else dep_stack
                )
                lines.append(f"  readonly {dep_stack.lower()}: {dep_stack_name};")
            lines.append("}")
            lines.append("")

        # Stack class
        if dependencies:
            lines.append(f"export class {stack_name} extends cdk.Stack {{")
            lines.append(
                f"  constructor(scope: Construct, id: string, props: {stack_name}Props) {{"
            )
        else:
            lines.append(f"export class {stack_name} extends cdk.Stack {{")
            lines.append(
                f"  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{"
            )

        lines.append("    super(scope, id, props);")
        lines.append("")

        # Add comment about the stack purpose
        lines.append(f"    // {stack_name} - {len(constructs)} construct(s)")
        lines.append("")

        # Instantiate constructs
        # Group by type for better organization
        constructs_by_type = {}
        for construct in constructs:
            resource_type = construct["type"]
            if resource_type not in constructs_by_type:
                constructs_by_type[resource_type] = []
            constructs_by_type[resource_type].append(construct)

        for resource_type, type_constructs in constructs_by_type.items():
            lines.append(f"    // {resource_type.capitalize()} resources")

            for construct in type_constructs:
                class_name = construct["class_name"]
                construct_name = construct["name"]
                construct_id = self._to_camel_case(construct_name)

                lines.append(f"    // const {construct_id} = new {class_name}(this, '{class_name}', {{")

                # Add props based on resource type
                if resource_type == "lambdas":
                    lines.append("    //   role: /* IAM role reference */")

                lines.append("    // });")
                lines.append(
                    f"    // TODO: Uncomment and configure {class_name} instantiation"
                )
                lines.append("")

        lines.append("  }")
        lines.append("}")

        return "\n".join(lines)

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        words = text.replace("-", " ").replace("_", " ").split()
        if not words:
            return text
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])
