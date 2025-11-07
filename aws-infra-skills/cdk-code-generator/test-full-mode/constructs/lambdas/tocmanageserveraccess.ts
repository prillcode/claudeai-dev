import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TocmanageserveraccessProps {
  role: iam.IRole;
}

/**
 * Lambda function: TocManageServerAccess
 * Runtime: python3.13
 * Handler: lambda_function.lambda_handler
 */
export class Tocmanageserveraccess {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TocmanageserveraccessProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'TocManageServerAccess',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/TocManageServerAccess'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(30),
      role: props.role,
      description: 'Used by Server Access Request Wizard in ToC. Manages Adding and Removing User Accounts from Servers and Databases.',
    });
  }
}
