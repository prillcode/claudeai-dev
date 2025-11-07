import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface IncodeapifunctionProps {
  role: iam.IRole;
}

/**
 * Lambda function: IncodeApiFunction
 * Runtime: dotnetcore3.1
 * Handler: incode-td-api::incode_td_api.IncodeApiFunction::GetRecordAsync
 */
export class Incodeapifunction {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: IncodeapifunctionProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'IncodeApiFunction',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'dotnetcore3.1',
      handler: 'incode-td-api::incode_td_api.IncodeApiFunction::GetRecordAsync',
      code: lambda.Code.fromAsset('./lambda/IncodeApiFunction'), // TODO: Update this path
      memorySize: 256,
      timeout: Duration.seconds(30),
      role: props.role,      environment: {
        IncodeAPI: 'IncodeAPI',
      },
      description: '',
    });
  }
}
