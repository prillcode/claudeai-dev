import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface StartEc2InstancesProps {
  role: iam.IRole;
}

/**
 * Lambda function: start-ec2-instances
 * Runtime: python3.13
 * Handler: lambda_function.lambda_handler
 */
export class StartEc2Instances {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: StartEc2InstancesProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'start-ec2-instances',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/start-ec2-instances'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(303),
      role: props.role,
      description: '',
    });
  }
}
