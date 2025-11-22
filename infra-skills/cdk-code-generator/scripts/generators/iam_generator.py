"""
IAM Role CDK Code Generator
"""

import json
from typing import Dict, Any, List


class IAMGenerator:
    """Generates CDK code for IAM roles."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, role: Dict[str, Any], mode: str) -> str:
        """Generate TypeScript CDK code for an IAM role."""
        if mode == 'reference':
            return self._generate_reference(role)
        else:
            return self._generate_full(role)

    def _generate_reference(self, role: Dict[str, Any]) -> str:
        """Generate reference-only import."""
        class_name = self._to_class_name(role['role_name'])
        role_name = role['role_name']
        role_arn = role['role_arn']

        code = f"""import * as iam from 'aws-cdk-lib/aws-iam';
import {{ Construct }} from 'constructs';

/**
 * Reference to existing IAM role: {role_name}
 * ARN: {role_arn}
 */
export class {class_name}Ref {{
  public readonly role: iam.IRole;

  constructor(scope: Construct, id: string) {{
    // Reference existing IAM role
    this.role = iam.Role.fromRoleArn(
      scope,
      id,
      '{role_arn}'
    );
  }}
}}
"""
        return code

    def _generate_full(self, role: Dict[str, Any]) -> str:
        """Generate full management construct."""
        class_name = self._to_class_name(role['role_name'])
        role_name = role['role_name']
        description = role.get('description', '')
        max_session_duration = role.get('max_session_duration', 3600)

        # Generate assume role policy (trust policy)
        assume_role_policy = role.get('assume_role_policy_document', {})
        assume_role_code = self._generate_assume_role_policy(assume_role_policy)

        # Generate managed policies
        managed_policies = role.get('attached_managed_policies', [])
        managed_policies_code = self._generate_managed_policies(managed_policies)

        # Generate inline policies
        inline_policies = role.get('inline_policies', [])
        inline_policies_code = self._generate_inline_policies(inline_policies)

        # Generate tags
        tags = role.get('tags', {})
        tags_code = self._generate_tags(tags)

        # Build description line
        description_code = ""
        if description:
            description_code = f"""      description: '{description}',"""

        code = f"""import * as iam from 'aws-cdk-lib/aws-iam';
import {{ Duration, Tags }} from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';

/**
 * IAM Role: {role_name}
 * Description: {description or 'N/A'}
 */
export class {class_name} {{
  public readonly role: iam.Role;

  constructor(scope: Construct, id: string) {{
    this.role = new iam.Role(scope, id, {{
      roleName: '{role_name}',{assume_role_code}{description_code}
      maxSessionDuration: Duration.seconds({max_session_duration}),
    }});
{managed_policies_code}{inline_policies_code}{tags_code}  }}
}}
"""
        return code

    def _generate_assume_role_policy(self, policy_doc: Dict[str, Any]) -> str:
        """Generate assume role policy (trust policy)."""
        if not policy_doc or not policy_doc.get('Statement'):
            return """
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),"""

        statements = policy_doc.get('Statement', [])
        if not statements:
            return """
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),"""

        # Get the first statement (usually there's only one for trust policies)
        statement = statements[0]
        principal = statement.get('Principal', {})

        # Handle service principal
        if 'Service' in principal:
            service = principal['Service']
            if isinstance(service, list):
                service = service[0]
            return f"""
      assumedBy: new iam.ServicePrincipal('{service}'),"""

        # Handle AWS principal
        if 'AWS' in principal:
            aws_principal = principal['AWS']
            if isinstance(aws_principal, list):
                aws_principal = aws_principal[0]
            return f"""
      assumedBy: new iam.ArnPrincipal('{aws_principal}'),"""

        # Handle federated principal
        if 'Federated' in principal:
            federated = principal['Federated']
            return f"""
      assumedBy: new iam.FederatedPrincipal('{federated}', {{}}, 'sts:AssumeRoleWithWebIdentity'),"""

        # Default to service principal
        return """
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),"""

    def _generate_managed_policies(self, managed_policies: List[Dict[str, Any]]) -> str:
        """Generate managed policy attachments."""
        if not managed_policies:
            return ""

        policy_lines = []
        for policy in managed_policies:
            policy_arn = policy.get('policy_arn', '')
            policy_name = policy.get('policy_name', '')

            # Check if it's an AWS managed policy
            if 'arn:aws:iam::aws:policy' in policy_arn:
                # Use fromAwsManagedPolicyName for AWS managed policies
                policy_lines.append(f"""
    // Attach AWS managed policy: {policy_name}
    this.role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('{policy_name}')
    );""")
            else:
                # Use fromManagedPolicyArn for customer managed policies
                policy_lines.append(f"""
    // Attach customer managed policy: {policy_name}
    this.role.addManagedPolicy(
      iam.ManagedPolicy.fromManagedPolicyArn(this, '{policy_name}Policy', '{policy_arn}')
    );""")

        return '\n'.join(policy_lines)

    def _generate_inline_policies(self, inline_policies: List[Dict[str, Any]]) -> str:
        """Generate inline policy statements."""
        if not inline_policies:
            return ""

        policy_lines = []
        for policy in inline_policies:
            policy_name = policy.get('policy_name', 'InlinePolicy')
            policy_doc = policy.get('policy_document', {})

            statements = policy_doc.get('Statement', [])
            if not statements:
                continue

            statement_code = self._generate_policy_statements(statements)

            policy_lines.append(f"""
    // Add inline policy: {policy_name}
    this.role.addToPolicy(new iam.PolicyStatement({{
{statement_code}
    }}));""")

        return '\n'.join(policy_lines)

    def _generate_policy_statements(self, statements: List[Dict[str, Any]]) -> str:
        """Generate policy statement configuration."""
        if not statements:
            return ""

        # For simplicity, handle the first statement
        # In a more complete implementation, we'd create multiple PolicyStatements
        statement = statements[0]

        effect = statement.get('Effect', 'Allow')
        actions = statement.get('Action', [])
        resources = statement.get('Resource', [])

        # Ensure actions and resources are lists
        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]

        # Format actions
        actions_str = ',\n        '.join([f"'{action}'" for action in actions])

        # Format resources
        resources_str = ',\n        '.join([f"'{resource}'" for resource in resources])

        code = f"""      effect: iam.Effect.{effect.upper()},
      actions: [
        {actions_str}
      ],
      resources: [
        {resources_str}
      ]"""

        # Handle conditions if present
        conditions = statement.get('Condition')
        if conditions:
            code += f""",
      // TODO: Add conditions: {json.dumps(conditions, indent=2)}"""

        return code

    def _generate_tags(self, tags: Dict[str, str]) -> str:
        """Generate tags."""
        if not tags:
            return ""

        tag_lines = []
        for key, value in tags.items():
            tag_lines.append(f"""    Tags.of(this.role).add('{key}', '{value}');""")

        if tag_lines:
            return '\n' + '\n'.join(tag_lines) + '\n'
        return ""

    @staticmethod
    def _to_class_name(role_name: str) -> str:
        """Convert role name to PascalCase class name."""
        # Split on hyphens and underscores
        parts = role_name.replace('-', '_').split('_')
        # Capitalize each part
        return ''.join(word.capitalize() for word in parts)
