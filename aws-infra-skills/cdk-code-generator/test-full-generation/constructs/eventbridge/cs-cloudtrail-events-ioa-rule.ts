import * as events from 'aws-cdk-lib/aws-events';
import { Construct } from 'constructs';

/**
 * Reference to existing EventBridge rule: cs-cloudtrail-events-ioa-rule
 * ARN: arn:aws:events:us-east-1:770885810964:rule/cs-cloudtrail-events-ioa-rule
 */
export class CsCloudtrailEventsIoaRuleRef {
  public readonly rule: events.IRule;

  constructor(scope: Construct, id: string) {
    // Reference existing EventBridge rule
    this.rule = events.Rule.fromRuleArn(
      scope,
      id,
      'arn:aws:events:us-east-1:770885810964:rule/cs-cloudtrail-events-ioa-rule'
    );
  }
}
