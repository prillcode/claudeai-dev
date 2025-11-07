import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface MscloudopsS3filesSignurlsProps {
  role: iam.IRole;
}

/**
 * Lambda function: mscloudops-s3files-signUrls
 * Runtime: python3.12
 * Handler: main.lambda_handler
 */
export class MscloudopsS3filesSignurls {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: MscloudopsS3filesSignurlsProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'mscloudops-s3files-signUrls',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'main.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/mscloudops-s3files-signUrls'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(20),
      role: props.role,
      description: 'Generates pre-signed download Urls for exising S3 files (pass bucket name and list of s3keys as payload).',
    });
  }
}
