import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface KnowledgebasepullProps {
  role: iam.IRole;
}

/**
 * Lambda function: KnowledgeBasePull
 * Runtime: python3.10
 * Handler: lambda_function.lambda_handler
 */
export class Knowledgebasepull {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: KnowledgebasepullProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'KnowledgeBasePull',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/KnowledgeBasePull'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(900),
      role: props.role,
      description: '',
    });
  }
}
