import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface MultipartuploadpurgeProps {
  role: iam.IRole;
}

/**
 * Lambda function: MultipartUploadPurge
 * Runtime: python3.12
 * Handler: index.lambda_handler
 */
export class Multipartuploadpurge {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: MultipartuploadpurgeProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'MultipartUploadPurge',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/MultipartUploadPurge'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(900),
      role: props.role,
      description: '',
    });
  }
}
