import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface IncodegatewayauthProps {
  role: iam.IRole;
}

/**
 * Lambda function: IncodeGateWayAuth
 * Runtime: dotnetcore3.1
 * Handler: IncodeGateWayAuth::IncodeGateWayAuth.Function::FunctionHandler
 */
export class Incodegatewayauth {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: IncodegatewayauthProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'IncodeGateWayAuth',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'dotnetcore3.1',
      handler: 'IncodeGateWayAuth::IncodeGateWayAuth.Function::FunctionHandler',
      code: lambda.Code.fromAsset('./lambda/IncodeGateWayAuth'), // TODO: Update this path
      memorySize: 256,
      timeout: Duration.seconds(30),
      role: props.role,      environment: {
        API_TOKEN: '72DEA3C15936E4BFCB67B06FD12FA4C9A1793ADCA6A13BD1E5C0AC5B1DFC3D13',
      },
      description: '',
    });
  }
}
