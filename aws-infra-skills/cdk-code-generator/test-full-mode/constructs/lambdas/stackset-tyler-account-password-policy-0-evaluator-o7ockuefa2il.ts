import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface StacksetTylerAccountPasswordPolicy0EvaluatorO7ockuefa2ilProps {
  role: iam.IRole;
}

/**
 * Lambda function: StackSet-Tyler-Account-Password-Policy-0-Evaluator-o7ockUEfA2Il
 * Runtime: python3.12
 * Handler: index.lambda_handler
 */
export class StacksetTylerAccountPasswordPolicy0EvaluatorO7ockuefa2il {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: StacksetTylerAccountPasswordPolicy0EvaluatorO7ockuefa2ilProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'StackSet-Tyler-Account-Password-Policy-0-Evaluator-o7ockUEfA2Il',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/StackSet-Tyler-Account-Password-Policy-0-Evaluator-o7ockUEfA2Il'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(60),
      role: props.role,      environment: {
        Target: 'arn:aws:sns:us-east-1:789937869171:tyler-ccs-Security-Notfications',
      },
      description: 'Evaluates and Corrects Account Password Policy.',
    });
  }
}
