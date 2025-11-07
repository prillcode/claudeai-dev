import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface MscloudopsCostdataReportingProps {
  role: iam.IRole;
}

/**
 * Lambda function: mscloudops-costdata-reporting
 * Runtime: python3.9
 * Handler: main.lambda_handler
 */
export class MscloudopsCostdataReporting {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: MscloudopsCostdataReportingProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'mscloudops-costdata-reporting',
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'main.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/mscloudops-costdata-reporting'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(30),
      role: props.role,
      description: 'Retrieves Cost Data from CostExplorer API in different formats based on CostDataFormat. Results are sent back to MSCloudOps Acct.',
    });
  }
}
