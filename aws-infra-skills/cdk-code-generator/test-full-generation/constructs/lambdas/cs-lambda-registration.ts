import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

/**
 * Reference to existing Lambda function: cs-lambda-registration
 * ARN: arn:aws:lambda:us-east-1:770885810964:function:cs-lambda-registration
 */
export class CsLambdaRegistrationRef {
  public readonly function: lambda.IFunction;

  constructor(scope: Construct, id: string) {
    // Reference existing Lambda function
    this.function = lambda.Function.fromFunctionArn(
      scope,
      id,
      'arn:aws:lambda:us-east-1:770885810964:function:cs-lambda-registration'
    );
  }
}
