import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface StacksetTylerCcsIamUserCreationAlTattletale3pzgaknk6fglProps {
  role: iam.IRole;
}

/**
 * Lambda function: StackSet-Tyler-CCS-IAM-User-Creation-Al-TattleTale-3PZgaknk6FGl
 * Runtime: python3.9
 * Handler: index.lambda_handler
 */
export class StacksetTylerCcsIamUserCreationAlTattletale3pzgaknk6fgl {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: StacksetTylerCcsIamUserCreationAlTattletale3pzgaknk6fglProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'StackSet-Tyler-CCS-IAM-User-Creation-Al-TattleTale-3PZgaknk6FGl',
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./lambda/StackSet-Tyler-CCS-IAM-User-Creation-Al-TattleTale-3PZgaknk6FGl'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(3),
      role: props.role,      environment: {
        Target: 'arn:aws:sns:us-east-1:789937869171:tyler-ccs-Aggregate-IAMUser-Creation-Notifications',
      },
      description: 'Forwards IAM User creations to global SNS Topic.',
    });
  }
}
