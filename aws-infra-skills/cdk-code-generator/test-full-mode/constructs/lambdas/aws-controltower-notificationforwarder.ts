import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface AwsControltowerNotificationforwarderProps {
  role: iam.IRole;
}

/**
 * Lambda function: aws-controltower-NotificationForwarder
 * Runtime: python3.13
 * Handler: index.lambda_handler
 */
export class AwsControltowerNotificationforwarder {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: AwsControltowerNotificationforwarderProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'aws-controltower-NotificationForwarder',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/aws-controltower-NotificationForwarder'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(60),
      role: props.role,      environment: {
        sns_arn: 'arn:aws:sns:us-east-1:789937869171:aws-controltower-AggregateSecurityNotifications',
      },
      description: 'SNS message forwarding function for aggregating account notifications.',
    });
  }
}
