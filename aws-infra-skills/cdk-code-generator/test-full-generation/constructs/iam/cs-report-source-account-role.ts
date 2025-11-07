import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

/**
 * Reference to existing IAM role: cs-report-source-account-role
 * ARN: arn:aws:iam::770885810964:role/cs-report-source-account-role
 */
export class CsReportSourceAccountRoleRef {
  public readonly role: iam.IRole;

  constructor(scope: Construct, id: string) {
    // Reference existing IAM role
    this.role = iam.Role.fromRoleArn(
      scope,
      id,
      'arn:aws:iam::770885810964:role/cs-report-source-account-role'
    );
  }
}
