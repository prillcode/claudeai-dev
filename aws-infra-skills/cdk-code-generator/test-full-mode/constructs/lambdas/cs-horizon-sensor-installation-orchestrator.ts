import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CsHorizonSensorInstallationOrchestratorProps {
  role: iam.IRole;
}

/**
 * Lambda function: cs-horizon-sensor-installation-orchestrator
 * Runtime: provided.al2
 * Handler: bootstrap
 */
export class CsHorizonSensorInstallationOrchestrator {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: CsHorizonSensorInstallationOrchestratorProps) {
    this.function = new lambda.Function(scope, id, {
      functionName: 'cs-horizon-sensor-installation-orchestrator',
      runtime: lambda.Runtime.FROM_IMAGE  // TODO: Map runtime 'provided.al2',
      handler: 'bootstrap',
      code: lambda.Code.fromAsset('./lambda/cs-horizon-sensor-installation-orchestrator'), // TODO: Update this path
      memorySize: 128,
      timeout: Duration.seconds(900),
      role: props.role,      environment: {
        CS_MODE: 'force_auth',
        CS_CLIENT_SECRET: '1W7ftBV0m24q8639KghozCGdbPFcu5lOpwAxvDUZ',
        CS_DEBUG_ENABLED: 'true',
        CS_CLIENT_ID: '8909b9e40eaa4b6b8f1e677fbc1d74d2',
      },
      description: '',
    });
  }
}
