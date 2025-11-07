import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CsharpHelloWorldProps {
  role: iam.IRole;
}

/**
 * Lambda function: csharp-hello-world
 * Runtime: dotnet8
 * Handler: LambdaTest::LambdaTest.LambdaHandler::handleRequest
 */
export class CsharpHelloWorld {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: CsharpHelloWorldProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'csharp-hello-world',
      runtime: lambda.Runtime.DOTNET_8,
      handler: 'LambdaTest::LambdaTest.LambdaHandler::handleRequest',
      code: lambda.Code.fromAsset('./lambda/csharp-hello-world'), // TODO: Update this path
      memorySize: 512,
      timeout: Duration.seconds(15),
      role: props.role,
      description: '',
    });
  }
}
