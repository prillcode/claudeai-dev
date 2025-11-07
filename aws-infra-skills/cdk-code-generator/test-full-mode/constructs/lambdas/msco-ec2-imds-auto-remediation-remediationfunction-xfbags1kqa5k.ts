import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface MscoEc2ImdsAutoRemediationRemediationfunctionXfbags1kqa5kProps {
  role: iam.IRole;
}

/**
 * Lambda function: msco-ec2-imds-auto-remediation-RemediationFunction-xFbaGs1kQa5k
 * Runtime: python3.12
 * Handler: index.lambda_handler
 */
export class MscoEc2ImdsAutoRemediationRemediationfunctionXfbags1kqa5k {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: MscoEc2ImdsAutoRemediationRemediationfunctionXfbags1kqa5kProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'msco-ec2-imds-auto-remediation-RemediationFunction-xFbaGs1kQa5k',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/msco-ec2-imds-auto-remediation-RemediationFunction-xFbaGs1kQa5k'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(10),
      role: props.role,
      description: 'Automated Remediation function courtesy of Corporate Cloud Services.',
    });
  }
}
