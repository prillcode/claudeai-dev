import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface TylerCcsConnectionlostInventoryFunction2Props {
  role: iam.IRole;
}

/**
 * Lambda function: tyler-ccs-connectionlost-inventory-function-2
 * Runtime: python3.9
 * Handler: index.lambda_handler
 */
export class TylerCcsConnectionlostInventoryFunction2 {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: TylerCcsConnectionlostInventoryFunction2Props) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'tyler-ccs-connectionlost-inventory-function-2',
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/tyler-ccs-connectionlost-inventory-function-2'), // TODO: Update this path
      memorySize: 10240,
      timeout: Duration.seconds(900),
      role: props.role,
      description: '',
    });
  }
}
