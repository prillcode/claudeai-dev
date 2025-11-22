"""
S3 Bucket CDK Code Generator
"""

import json
from typing import Dict, Any, List


class S3Generator:
    """Generates CDK code for S3 buckets."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, bucket: Dict[str, Any], mode: str) -> str:
        """Generate TypeScript CDK code for an S3 bucket."""
        if mode == 'reference':
            return self._generate_reference(bucket)
        else:
            return self._generate_full(bucket)

    def _generate_reference(self, bucket: Dict[str, Any]) -> str:
        """Generate reference-only import."""
        class_name = self._to_class_name(bucket['bucket_name'])
        bucket_name = bucket['bucket_name']
        bucket_arn = bucket.get('bucket_arn', f"arn:aws:s3:::{bucket_name}")

        code = f"""import * as s3 from 'aws-cdk-lib/aws-s3';
import {{ Construct }} from 'constructs';

/**
 * Reference to existing S3 bucket: {bucket_name}
 * ARN: {bucket_arn}
 */
export class {class_name}Ref {{
  public readonly bucket: s3.IBucket;

  constructor(scope: Construct, id: string) {{
    // Reference existing S3 bucket
    this.bucket = s3.Bucket.fromBucketName(
      scope,
      id,
      '{bucket_name}'
    );
  }}
}}
"""
        return code

    def _generate_full(self, bucket: Dict[str, Any]) -> str:
        """Generate full management construct."""
        class_name = self._to_class_name(bucket['bucket_name'])
        bucket_name = bucket['bucket_name']

        # Get versioning
        versioned = bucket.get('versioning', False)
        versioning_code = f"""      versioned: {str(versioned).lower()},"""

        # Get encryption
        encryption = bucket.get('encryption', {})
        encryption_code = self._generate_encryption(encryption)

        # Get public access block
        public_access = bucket.get('public_access_block', {})
        public_access_code = self._generate_public_access_block(public_access)

        # Get lifecycle rules
        lifecycle_rules = bucket.get('lifecycle_rules', [])
        lifecycle_code = self._generate_lifecycle_rules(lifecycle_rules)

        # Get CORS
        cors_rules = bucket.get('cors_rules', [])
        cors_code = self._generate_cors(cors_rules)

        # Get tags
        tags = bucket.get('tags', {})
        tags_code = self._generate_tags(tags)

        # Build imports
        imports = """import * as s3 from 'aws-cdk-lib/aws-s3';
import {{ RemovalPolicy, Tags, Duration }} from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';"""

        code = f"""{imports}

/**
 * S3 Bucket: {bucket_name}
 * Versioning: {versioned}
 * Encryption: {encryption.get('encryption_type', 'NONE')}
 */
export class {class_name} {{
  public readonly bucket: s3.Bucket;

  constructor(scope: Construct, id: string) {{
    this.bucket = new s3.Bucket(scope, id, {{
      bucketName: '{bucket_name}',{versioning_code}{encryption_code}{public_access_code}
      removalPolicy: RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
    }});
{lifecycle_code}{cors_code}{tags_code}  }}
}}
"""
        return code

    def _generate_encryption(self, encryption: Dict[str, Any]) -> str:
        """Generate encryption configuration."""
        if not encryption or encryption.get('encryption_type') == 'NONE':
            return """
      encryption: s3.BucketEncryption.UNENCRYPTED,"""

        encryption_type = encryption.get('encryption_type', 'NONE')

        if encryption_type == 'AES256':
            return """
      encryption: s3.BucketEncryption.S3_MANAGED,"""
        elif encryption_type == 'aws:kms':
            kms_key_id = encryption.get('kms_master_key_id', '')
            if kms_key_id:
                return f"""
      encryption: s3.BucketEncryption.KMS,
      // TODO: Import KMS key: {kms_key_id}"""
            else:
                return """
      encryption: s3.BucketEncryption.KMS_MANAGED,"""

        return """
      encryption: s3.BucketEncryption.S3_MANAGED,"""

    def _generate_public_access_block(self, public_access: Dict[str, Any]) -> str:
        """Generate public access block configuration."""
        if not public_access:
            # Default to most restrictive settings
            return """
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,"""

        block_public_acls = public_access.get('BlockPublicAcls', True)
        ignore_public_acls = public_access.get('IgnorePublicAcls', True)
        block_public_policy = public_access.get('BlockPublicPolicy', True)
        restrict_public_buckets = public_access.get('RestrictPublicBuckets', True)

        # If all are true, use BLOCK_ALL
        if all([block_public_acls, ignore_public_acls, block_public_policy, restrict_public_buckets]):
            return """
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,"""

        # Otherwise, create custom configuration
        return f"""
      blockPublicAccess: new s3.BlockPublicAccess({{
        blockPublicAcls: {str(block_public_acls).lower()},
        ignorePublicAcls: {str(ignore_public_acls).lower()},
        blockPublicPolicy: {str(block_public_policy).lower()},
        restrictPublicBuckets: {str(restrict_public_buckets).lower()},
      }}),"""

    def _generate_lifecycle_rules(self, lifecycle_rules: List[Dict[str, Any]]) -> str:
        """Generate lifecycle rules."""
        if not lifecycle_rules:
            return ""

        rule_lines = []
        for rule in lifecycle_rules:
            rule_id = rule.get('ID', 'Rule')
            status = rule.get('Status', 'Enabled')
            prefix = rule.get('Prefix', '')

            if status != 'Enabled':
                continue

            # Get transitions
            transitions = rule.get('Transitions', [])
            expiration = rule.get('Expiration', {})

            rule_code = f"""
    // Lifecycle rule: {rule_id}
    this.bucket.addLifecycleRule({{
      id: '{rule_id}',"""

            if prefix:
                rule_code += f"""
      prefix: '{prefix}',"""

            # Add transitions
            if transitions:
                for transition in transitions:
                    days = transition.get('Days')
                    storage_class = transition.get('StorageClass', 'GLACIER')
                    if days:
                        rule_code += f"""
      transitions: [{{
        storageClass: s3.StorageClass.{storage_class},
        transitionAfter: Duration.days({days}),
      }}],"""

            # Add expiration
            if expiration:
                expiration_days = expiration.get('Days')
                if expiration_days:
                    rule_code += f"""
      expiration: Duration.days({expiration_days}),"""

            rule_code += """
    });"""
            rule_lines.append(rule_code)

        return '\n'.join(rule_lines)

    def _generate_cors(self, cors_rules: List[Dict[str, Any]]) -> str:
        """Generate CORS configuration."""
        if not cors_rules:
            return ""

        cors_code = []
        for rule in cors_rules:
            allowed_methods = rule.get('AllowedMethods', [])
            allowed_origins = rule.get('AllowedOrigins', [])
            allowed_headers = rule.get('AllowedHeaders', [])
            max_age = rule.get('MaxAgeSeconds', 3000)

            methods_str = ', '.join([f's3.HttpMethods.{method.upper()}' for method in allowed_methods])
            origins_str = ', '.join([f"'{origin}'" for origin in allowed_origins])

            cors_code.append(f"""
    // Add CORS rule
    this.bucket.addCorsRule({{
      allowedMethods: [{methods_str}],
      allowedOrigins: [{origins_str}],
      allowedHeaders: {allowed_headers},
      maxAge: {max_age},
    }});""")

        return '\n'.join(cors_code)

    def _generate_tags(self, tags: Dict[str, str]) -> str:
        """Generate tags."""
        if not tags:
            return ""

        tag_lines = []
        for key, value in tags.items():
            tag_lines.append(f"""    Tags.of(this.bucket).add('{key}', '{value}');""")

        if tag_lines:
            return '\n' + '\n'.join(tag_lines) + '\n'
        return ""

    @staticmethod
    def _to_class_name(bucket_name: str) -> str:
        """Convert bucket name to PascalCase class name."""
        # Split on hyphens, dots, and underscores
        parts = bucket_name.replace('.', '-').replace('_', '-').split('-')
        # Capitalize each part
        return ''.join(word.capitalize() for word in parts if word)
