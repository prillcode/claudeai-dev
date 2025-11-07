import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TocAutomationDevLambdaProps {
  role: iam.IRole;
}

/**
 * Lambda function: Toc-automation-dev-lambda
 * Runtime: python3.13
 * Handler: lambda_function.lambda_handler
 */
export class TocAutomationDevLambda {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TocAutomationDevLambdaProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'Toc-automation-dev-lambda',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'python3.13',
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/Toc-automation-dev-lambda'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(303),
      role: props.role,      environment: {
        DYNAMODB_SCHEDULE_GROUPS_TABLE: 'TocScheduleGroups-dev',
        DYNAMODB_RELEASE_INFO_TABLE: 'TocSEPReleaseInfo-dev',
      },
      description: '',
    });
  }
}
