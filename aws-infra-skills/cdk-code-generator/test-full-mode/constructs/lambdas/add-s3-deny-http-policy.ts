import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface AddS3DenyHttpPolicyProps {
  role: iam.IRole;
}

/**
 * Lambda function: add-s3-deny-http-policy
 * Runtime: python3.12
 * Handler: s3-create-policy.lambda_handler
 */
export class AddS3DenyHttpPolicy {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: AddS3DenyHttpPolicyProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'add-s3-deny-http-policy',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 's3-create-policy.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/add-s3-deny-http-policy'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(60),
      role: props.role,
      description: 'Lambda function to add deny http bucket policy',
    });
  }
}
