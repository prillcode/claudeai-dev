import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface StacksetCcsbillinganomalydAnomalymonitordetector5bk4iz0v6bonProps {
  role: iam.IRole;
}

/**
 * Lambda function: StackSet-CCSBillingAnomalyD-AnomalyMonitorDetector-5bk4IZ0V6bOn
 * Runtime: python3.13
 * Handler: index.lambda_handler
 */
export class StacksetCcsbillinganomalydAnomalymonitordetector5bk4iz0v6bon {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: StacksetCcsbillinganomalydAnomalymonitordetector5bk4iz0v6bonProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'StackSet-CCSBillingAnomalyD-AnomalyMonitorDetector-5bk4IZ0V6bOn',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/StackSet-CCSBillingAnomalyD-AnomalyMonitorDetector-5bk4IZ0V6bOn'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(120),
      role: props.role,      environment: {
        RETRY_BASE_SECONDS: '0.5',
        RETRY_CAP_SECONDS: '4',
        AWS_MAX_ATTEMPTS: '10',
        INITIAL_JITTER_MAX: '5',
        AWS_RETRY_MODE: 'adaptive',
        RETRY_MAX_ATTEMPTS: '8',
      },
      description: 'Locates Anomaly Monitors for CloudFormation.',
    });
  }
}
