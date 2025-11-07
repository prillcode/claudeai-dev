import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TocSsmAutomationDevProps {
  role: iam.IRole;
}

/**
 * Lambda function: toc-ssm-automation-dev
 * Runtime: nodejs20.x
 * Handler: dist/index.handler
 */
export class TocSsmAutomationDev {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TocSsmAutomationDevProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'toc-ssm-automation-dev',
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'dist/index.handler',
      code: lambda.Code.fromAsset('./lambda/toc-ssm-automation-dev'), // TODO: Update this path
      memorySize: 256,
      timeout: Duration.seconds(300),
      role: props.role,      environment: {
        ENVIRONMENT: 'dev',
      },
      description: 'SSM Automation Lambda - Cross-account execution - dev',
    });
  }
}
