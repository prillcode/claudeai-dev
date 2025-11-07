import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface SepupdatecrawlerDevProps {
  role: iam.IRole;
}

/**
 * Lambda function: SepUpdateCrawler-dev
 * Runtime: python3.12
 * Handler: lambda_function.lambda_handler
 */
export class SepupdatecrawlerDev {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: SepupdatecrawlerDevProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'SepUpdateCrawler-dev',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/SepUpdateCrawler-dev'), // TODO: Update this path
      memorySize: 512,
      timeout: Duration.seconds(900),
      role: props.role,      environment: {
        DYNAMODB_SCHEDULE_GROUPS_TABLE: 'TocScheduleGroups-dev',
        DYNAMODB_RELEASE_INFO_TABLE: 'TocSEPReleaseInfo-dev',
        ENVIRONMENT: 'dev',
      },
      description: 'SEP Update Crawler Lambda - dev',
    });
  }
}
