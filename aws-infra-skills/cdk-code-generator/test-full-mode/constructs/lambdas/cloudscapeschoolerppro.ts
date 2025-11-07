import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CloudscapeschoolerpproProps {
  role: iam.IRole;
}

/**
 * Lambda function: CloudScapeSchoolErpPro
 * Runtime: python3.13
 * Handler: lambda_function.lambda_handler
 */
export class Cloudscapeschoolerppro {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: CloudscapeschoolerpproProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'CloudScapeSchoolErpPro',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/CloudScapeSchoolErpPro'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(303),
      role: props.role,      environment: {
        DYNAMODB_SCHEDULE_GROUPS_TABLE: 'TocScheduleGroups-dev',
      },
      description: '',
    });
  }
}
