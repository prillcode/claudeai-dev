import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface Erppro10getkbbydatasetnameProps {
  role: iam.IRole;
}

/**
 * Lambda function: ERPPro10GetKbByDataSetName
 * Runtime: python3.13
 * Handler: lambda_function.lambda_handler
 */
export class Erppro10getkbbydatasetname {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: Erppro10getkbbydatasetnameProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'ERPPro10GetKbByDataSetName',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/ERPPro10GetKbByDataSetName'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(900),
      role: props.role,
      description: '',
    });
  }
}
