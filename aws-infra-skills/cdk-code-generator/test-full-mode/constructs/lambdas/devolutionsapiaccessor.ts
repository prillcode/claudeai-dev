import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface DevolutionsapiaccessorProps {
  role: iam.IRole;
}

/**
 * Lambda function: DevolutionsAPIAccessor
 * Runtime: python3.7
 * Handler: lambda_function.lambda_handler
 */
export class Devolutionsapiaccessor {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: DevolutionsapiaccessorProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'DevolutionsAPIAccessor',
      runtime: lambda.Runtime.PYTHON_3_7,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/DevolutionsAPIAccessor'), // TODO: Update this path
      memorySize: 512,
      timeout: Duration.seconds(10),
      role: props.role,
      description: 'A simple backend (read/write to DynamoDB) with a RESTful API endpoint using Amazon API Gateway.',
    });
  }
}
