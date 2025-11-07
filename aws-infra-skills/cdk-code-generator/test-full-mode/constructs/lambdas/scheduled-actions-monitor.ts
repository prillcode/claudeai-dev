import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface ScheduledActionsMonitorProps {
  role: iam.IRole;
}

/**
 * Lambda function: scheduled-actions-monitor
 * Runtime: python3.13
 * Handler: lambda_function.lambda_handler
 */
export class ScheduledActionsMonitor {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: ScheduledActionsMonitorProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'scheduled-actions-monitor',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/scheduled-actions-monitor'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(305),
      role: props.role,      environment: {
        SNS_TOPIC_ARN: 'arn:aws:sns:us-east-1:770885810964:ScheduledActionsTopic',
      },
      description: '',
    });
  }
}
