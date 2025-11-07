import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CloudscapeSoftwareDeliveryProps {
  role: iam.IRole;
}

/**
 * Lambda function: cloudscape-software-delivery
 * Runtime: python3.12
 * Handler: cloudscape-software-delivery.lambda_handler
 */
export class CloudscapeSoftwareDelivery {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: CloudscapeSoftwareDeliveryProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'cloudscape-software-delivery',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'cloudscape-software-delivery.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/cloudscape-software-delivery'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(300),
      role: props.role,      environment: {
        ddb_log_table: 'cloudscape-software-delivery-logs',
        source_queue: 'https://sqs.us-east-1.amazonaws.com/770885810964/CloudscapeSoftwareDelivery.fifo',
      },
      description: '',
    });
  }
}
