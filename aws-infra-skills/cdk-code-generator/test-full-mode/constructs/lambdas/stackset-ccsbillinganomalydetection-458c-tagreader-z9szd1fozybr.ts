import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface StacksetCcsbillinganomalydetection458cTagreaderZ9szd1fozybrProps {
  role: iam.IRole;
}

/**
 * Lambda function: StackSet-CCSBillingAnomalyDetection-458c-TagReader-z9Szd1FOzYbR
 * Runtime: python3.13
 * Handler: index.lambda_handler
 */
export class StacksetCcsbillinganomalydetection458cTagreaderZ9szd1fozybr {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: StacksetCcsbillinganomalydetection458cTagreaderZ9szd1fozybrProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'StackSet-CCSBillingAnomalyDetection-458c-TagReader-z9Szd1FOzYbR',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/StackSet-CCSBillingAnomalyDetection-458c-TagReader-z9Szd1FOzYbR'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(900),
      role: props.role,      environment: {
        RETRY_BASE_SECONDS: '1',
        RETRY_CAP_SECONDS: '8',
        AWS_MAX_ATTEMPTS: '10',
        INITIAL_JITTER_MAX: '20',
        AWS_RETRY_MODE: 'adaptive',
        RETRY_MAX_ATTEMPTS: '8',
        varMonitorArnList: 'arn:aws:ce::770885810964:anomalymonitor/5effd8f3-c2a2-43e6-b6da-92528183ca59',
      },
      description: 'Deploys Tag Based Anomaly Monitor(s).',
    });
  }
}
