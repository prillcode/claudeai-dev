import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CloudscapeAppForwarderProps {
  role: iam.IRole;
}

/**
 * Lambda function: cloudscape-app-forwarder
 * Runtime: python3.12
 * Handler: lambda_function.lambda_handler
 */
export class CloudscapeAppForwarder {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: CloudscapeAppForwarderProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'cloudscape-app-forwarder',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/cloudscape-app-forwarder'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(15),
      role: props.role,      environment: {
        tcm_prod_assume_role: ''arn:aws:iam::765094771410:role/service-role/StepFunctions-cloudscape-software-delivery-role-ee3nj77o1'',
      },
      description: '',
    });
  }
}
