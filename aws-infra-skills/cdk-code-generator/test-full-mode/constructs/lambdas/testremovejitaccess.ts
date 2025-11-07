import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TestremovejitaccessProps {
  role: iam.IRole;
}

/**
 * Lambda function: TESTRemoveJITAccess
 * Runtime: python3.12
 * Handler: lambda_function.lambda_handler
 */
export class Testremovejitaccess {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TestremovejitaccessProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'TESTRemoveJITAccess',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/TESTRemoveJITAccess'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(3),
      role: props.role,
      description: '',
    });
  }
}
