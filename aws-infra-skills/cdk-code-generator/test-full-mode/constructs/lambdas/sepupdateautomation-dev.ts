import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface SepupdateautomationDevProps {
  role: iam.IRole;
}

/**
 * Lambda function: SepUpdateAutomation-dev
 * Runtime: python3.12
 * Handler: lambda_function.lambda_handler
 */
export class SepupdateautomationDev {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: SepupdateautomationDevProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'SepUpdateAutomation-dev',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/SepUpdateAutomation-dev'), // TODO: Update this path
      memorySize: 512,
      timeout: Duration.seconds(900),
      role: props.role,      environment: {
        DYNAMODB_SCHEDULE_GROUPS_TABLE: 'TocScheduleGroups-dev',
        DYNAMODB_RELEASE_INFO_TABLE: 'TocSEPReleaseInfo-dev',
        ENVIRONMENT: 'dev',
      },
      description: 'SEP Update Automation Lambda - dev',
    });
  }
}
