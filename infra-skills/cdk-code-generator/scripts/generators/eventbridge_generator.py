"""
EventBridge Rule CDK Code Generator
"""

import json
from typing import Dict, Any, List


class EventBridgeGenerator:
    """Generates CDK code for EventBridge rules."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, rule: Dict[str, Any], mode: str) -> str:
        """Generate TypeScript CDK code for an EventBridge rule."""
        if mode == 'reference':
            return self._generate_reference(rule)
        else:
            return self._generate_full(rule)

    def _generate_reference(self, rule: Dict[str, Any]) -> str:
        """Generate reference-only import."""
        class_name = self._to_class_name(rule['rule_name'])
        rule_name = rule['rule_name']
        rule_arn = rule['rule_arn']

        code = f"""import * as events from 'aws-cdk-lib/aws-events';
import {{ Construct }} from 'constructs';

/**
 * Reference to existing EventBridge rule: {rule_name}
 * ARN: {rule_arn}
 */
export class {class_name}Ref {{
  public readonly rule: events.IRule;

  constructor(scope: Construct, id: string) {{
    // Reference existing EventBridge rule
    this.rule = events.Rule.fromRuleArn(
      scope,
      id,
      '{rule_arn}'
    );
  }}
}}
"""
        return code

    def _generate_full(self, rule: Dict[str, Any]) -> str:
        """Generate full management construct."""
        class_name = self._to_class_name(rule['rule_name'])
        rule_name = rule['rule_name']
        description = rule.get('description', '')
        state = rule.get('state', 'ENABLED')
        event_bus_name = rule.get('event_bus_name', 'default')

        # Get event pattern or schedule
        event_pattern = rule.get('event_pattern')
        schedule_expression = rule.get('schedule_expression')

        # Generate rule configuration
        if event_pattern:
            pattern_code = self._generate_event_pattern(event_pattern)
        elif schedule_expression:
            pattern_code = self._generate_schedule(schedule_expression)
        else:
            pattern_code = """      // TODO: Add event pattern or schedule"""

        # Get targets
        targets = rule.get('targets', [])
        targets_code = self._generate_targets(targets)

        # Get tags
        tags = rule.get('tags', {})
        tags_code = self._generate_tags(tags)

        # Build description line
        description_code = ""
        if description:
            description_code = f"""      description: '{description}',"""

        # Build enabled/disabled
        enabled = state == 'ENABLED'
        enabled_code = f"""      enabled: {str(enabled).lower()},"""

        # Event bus
        event_bus_code = ""
        if event_bus_name and event_bus_name != 'default':
            event_bus_code = f"""
      // TODO: Reference event bus: {event_bus_name}
      // eventBus: events.EventBus.fromEventBusName(this, 'EventBus', '{event_bus_name}'),"""

        code = f"""import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {{ Tags }} from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';

/**
 * EventBridge Rule: {rule_name}
 * State: {state}
 * Event Bus: {event_bus_name}
 */
export class {class_name} {{
  public readonly rule: events.Rule;

  constructor(scope: Construct, id: string) {{
    this.rule = new events.Rule(scope, id, {{
      ruleName: '{rule_name}',{description_code}{enabled_code}{event_bus_code}
{pattern_code}
    }});
{targets_code}{tags_code}  }}
}}
"""
        return code

    def _generate_event_pattern(self, event_pattern: Dict[str, Any]) -> str:
        """Generate event pattern configuration."""
        if not event_pattern:
            return """      // TODO: Add event pattern"""

        # Convert event pattern to CDK EventPattern format
        # This is a simplified version - full implementation would handle all pattern types
        pattern_json = json.dumps(event_pattern, indent=6)

        return f"""      eventPattern: {pattern_json},"""

    def _generate_schedule(self, schedule_expression: str) -> str:
        """Generate schedule expression."""
        if not schedule_expression:
            return """      // TODO: Add schedule"""

        # Check if it's a rate or cron expression
        if schedule_expression.startswith('rate('):
            # Extract rate value, e.g., "rate(5 minutes)" -> "5 minutes"
            rate_value = schedule_expression[5:-1]  # Remove "rate(" and ")"
            return f"""      schedule: events.Schedule.rate(cdk.Duration.{rate_value.replace(' ', '')}),"""
        elif schedule_expression.startswith('cron('):
            # It's a cron expression
            return f"""      schedule: events.Schedule.expression('{schedule_expression}'),"""
        else:
            return f"""      schedule: events.Schedule.expression('{schedule_expression}'),"""

    def _generate_targets(self, targets: List[Dict[str, Any]]) -> str:
        """Generate rule targets."""
        if not targets:
            return ""

        target_lines = []
        for target in targets:
            target_id = target.get('id', 'Target')
            target_arn = target.get('arn', '')
            role_arn = target.get('role_arn')

            # Determine target type from ARN
            if 'lambda' in target_arn:
                target_lines.append(f"""
    // Add Lambda target: {target_id}
    // TODO: Import Lambda function from ARN: {target_arn}
    // this.rule.addTarget(new targets.LambdaFunction(lambdaFunction));""")

            elif 'event-bus' in target_arn:
                target_lines.append(f"""
    // Add EventBridge target: {target_id}
    // TODO: Import event bus from ARN: {target_arn}
    // this.rule.addTarget(new targets.EventBus(eventBus));""")

            elif 'kinesis:stream' in target_arn:
                target_lines.append(f"""
    // Add Kinesis stream target: {target_id}
    // TODO: Import Kinesis stream from ARN: {target_arn}
    // this.rule.addTarget(new targets.KinesisStream(stream));""")

            elif 'sqs' in target_arn:
                target_lines.append(f"""
    // Add SQS queue target: {target_id}
    // TODO: Import SQS queue from ARN: {target_arn}
    // this.rule.addTarget(new targets.SqsQueue(queue));""")

            elif 'sns' in target_arn:
                target_lines.append(f"""
    // Add SNS topic target: {target_id}
    // TODO: Import SNS topic from ARN: {target_arn}
    // this.rule.addTarget(new targets.SnsTopic(topic));""")

            elif 'states' in target_arn:
                target_lines.append(f"""
    // Add Step Functions target: {target_id}
    // TODO: Import Step Functions state machine from ARN: {target_arn}
    // this.rule.addTarget(new targets.SfnStateMachine(stateMachine));""")

            else:
                target_lines.append(f"""
    // Add target: {target_id}
    // ARN: {target_arn}
    // TODO: Configure target based on ARN type""")

            if role_arn:
                target_lines[-1] += f"""
    // Role ARN: {role_arn}"""

        return '\n'.join(target_lines)

    def _generate_tags(self, tags: Dict[str, str]) -> str:
        """Generate tags."""
        if not tags:
            return ""

        tag_lines = []
        for key, value in tags.items():
            tag_lines.append(f"""    Tags.of(this.rule).add('{key}', '{value}');""")

        if tag_lines:
            return '\n' + '\n'.join(tag_lines) + '\n'
        return ""

    @staticmethod
    def _to_class_name(rule_name: str) -> str:
        """Convert rule name to PascalCase class name."""
        # Split on hyphens and underscores
        parts = rule_name.replace('-', '_').split('_')
        # Capitalize each part
        return ''.join(word.capitalize() for word in parts)
