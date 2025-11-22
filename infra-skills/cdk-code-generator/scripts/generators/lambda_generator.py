"""
Lambda Function CDK Code Generator
"""

from typing import Dict, Any


class LambdaGenerator:
    """Generates CDK code for Lambda functions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, lambda_func: Dict[str, Any], mode: str) -> str:
        """Generate TypeScript CDK code for a Lambda function."""
        if mode == 'reference':
            return self._generate_reference(lambda_func)
        else:
            return self._generate_full(lambda_func)

    def _generate_reference(self, lambda_func: Dict[str, Any]) -> str:
        """Generate reference-only import."""
        class_name = self._to_class_name(lambda_func['function_name'])
        function_name = lambda_func['function_name']
        function_arn = lambda_func['function_arn']

        code = f"""import * as lambda from 'aws-cdk-lib/aws-lambda';
import {{ Construct }} from 'constructs';

/**
 * Reference to existing Lambda function: {function_name}
 * ARN: {function_arn}
 */
export class {class_name}Ref {{
  public readonly function: lambda.IFunction;

  constructor(scope: Construct, id: string) {{
    // Reference existing Lambda function
    this.function = lambda.Function.fromFunctionArn(
      scope,
      id,
      '{function_arn}'
    );
  }}
}}
"""
        return code

    def _generate_full(self, lambda_func: Dict[str, Any]) -> str:
        """Generate full management construct."""
        class_name = self._to_class_name(lambda_func['function_name'])
        function_name = lambda_func['function_name']
        runtime = self._map_runtime(lambda_func['runtime'])
        handler = lambda_func['handler']
        memory_size = lambda_func['memory_size']
        timeout = lambda_func['timeout']
        description = lambda_func.get('description', '')
        env_vars = lambda_func.get('environment_variables', {})

        # Build environment variables
        env_lines = []
        if env_vars:
            for key, value in env_vars.items():
                env_lines.append(f"        {key}: '{value}',")

        env_block = ""
        if env_lines:
            env_block = f"""
      environment: {{
{chr(10).join(env_lines)}
      }},"""

        code = f"""import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import {{ Duration }} from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';

export interface {class_name}Props {{
  role: iam.IRole;
}}

/**
 * Lambda function: {function_name}
 * Runtime: {lambda_func['runtime']}
 * Handler: {handler}
 */
export class {class_name} {{
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: {class_name}Props) {{
    this.function = new lambda.Function(scope, id, {{
      functionName: '{function_name}',
      runtime: {runtime},
      handler: '{handler}',
      code: lambda.Code.fromAsset('./lambda/{function_name}'), // TODO: Update this path
      memorySize: {memory_size},
      timeout: Duration.seconds({timeout}),
      role: props.role,{env_block}
      description: '{description}',
    }});
  }}
}}
"""
        return code

    @staticmethod
    def _to_class_name(function_name: str) -> str:
        """Convert function name to PascalCase class name."""
        # Split on hyphens and underscores
        parts = function_name.replace('-', '_').split('_')
        # Capitalize each part
        return ''.join(word.capitalize() for word in parts)

    @staticmethod
    def _map_runtime(runtime_str: str) -> str:
        """Map AWS runtime string to CDK Runtime enum."""
        runtime_map = {
            'python3.12': 'lambda.Runtime.PYTHON_3_12',
            'python3.11': 'lambda.Runtime.PYTHON_3_11',
            'python3.10': 'lambda.Runtime.PYTHON_3_10',
            'python3.9': 'lambda.Runtime.PYTHON_3_9',
            'python3.8': 'lambda.Runtime.PYTHON_3_8',
            'python3.7': 'lambda.Runtime.PYTHON_3_7',
            'nodejs20.x': 'lambda.Runtime.NODEJS_20_X',
            'nodejs18.x': 'lambda.Runtime.NODEJS_18_X',
            'nodejs16.x': 'lambda.Runtime.NODEJS_16_X',
            'nodejs14.x': 'lambda.Runtime.NODEJS_14_X',
            'java17': 'lambda.Runtime.JAVA_17',
            'java11': 'lambda.Runtime.JAVA_11',
            'java8.al2': 'lambda.Runtime.JAVA_8_CORRETTO',
            'dotnet6': 'lambda.Runtime.DOTNET_6',
            'dotnet8': 'lambda.Runtime.DOTNET_8',
            'go1.x': 'lambda.Runtime.GO_1_X',
            'ruby3.2': 'lambda.Runtime.RUBY_3_2',
            'ruby2.7': 'lambda.Runtime.RUBY_2_7',
        }

        return runtime_map.get(runtime_str, f"lambda.Runtime.FROM_IMAGE  // TODO: Map runtime '{runtime_str}'")
