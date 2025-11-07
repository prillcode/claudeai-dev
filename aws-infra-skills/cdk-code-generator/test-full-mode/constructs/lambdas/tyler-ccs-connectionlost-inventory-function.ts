import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TylerCcsConnectionlostInventoryFunctionProps {
  role: iam.IRole;
}

/**
 * Lambda function: tyler-ccs-connectionlost-inventory-function
 * Runtime: python3.9
 * Handler: index.lambda_handler
 */
export class TylerCcsConnectionlostInventoryFunction {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TylerCcsConnectionlostInventoryFunctionProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'tyler-ccs-connectionlost-inventory-function',
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/tyler-ccs-connectionlost-inventory-function'), // TODO: Update this path
      memorySize: 10240,
      timeout: Duration.seconds(900),
      role: props.role,
      description: '',
    });
  }
}
