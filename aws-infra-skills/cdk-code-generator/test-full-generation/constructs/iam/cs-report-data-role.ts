import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

/**
 * Reference to existing IAM role: cs-report-data-role
 * ARN: arn:aws:iam::770885810964:role/cs-report-data-role
 */
export class CsReportDataRoleRef {
  public readonly role: iam.IRole;

  constructor(scope: Construct, id: string) {
    // Reference existing IAM role
    this.role = iam.Role.fromRoleArn(
      scope,
      id,
      'arn:aws:iam::770885810964:role/cs-report-data-role'
    );
  }
}
