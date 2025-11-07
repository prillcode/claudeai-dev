import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TocappupdateschedulerunnerDevProps {
  role: iam.IRole;
}

/**
 * Lambda function: TocAppUpdateScheduleRunner-dev
 * Runtime: nodejs20.x
 * Handler: index.handler
 */
export class TocappupdateschedulerunnerDev {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TocappupdateschedulerunnerDevProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'TocAppUpdateScheduleRunner-dev',
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('./lambda/TocAppUpdateScheduleRunner-dev'), // TODO: Update this path
      memorySize: 256,
      timeout: Duration.seconds(300),
      role: props.role,      environment: {
        ENVIRONMENT: 'dev',
        DYNAMODB_TABLE_NAME: 'TocAppUpdateScheduleGroups-dev',
      },
      description: 'TOC App Update Schedule Runner - dev',
    });
  }
}
