import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CsLambdaRegistrationProps {
  role: iam.IRole;
}

/**
 * Lambda function: cs-lambda-registration
 * Runtime: provided.al2
 * Handler: bootstrap
 */
export class CsLambdaRegistration {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: CsLambdaRegistrationProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'cs-lambda-registration',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'provided.al2',
      handler: 'bootstrap',
      code: lambda.Code.fromAsset('./lambda/cs-lambda-registration'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(605),
      role: props.role,      environment: {
        CS_CURRENT_ACCOUNT: '770885810964',
        CS_DEBUG_ENABLED: 'true',
      },
      description: '',
    });
  }
}
