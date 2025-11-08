# Troubleshooting Guide

This guide covers common issues encountered during the AWS to CDK import workflow and their solutions.

## Table of Contents

1. [Phase 1: Resource Discovery Issues](#phase-1-resource-discovery-issues)
2. [Phase 2: Code Generation Issues](#phase-2-code-generation-issues)
3. [Phase 3: Stack Organization Issues](#phase-3-stack-organization-issues)
4. [Phase 4: Import Configuration Issues](#phase-4-import-configuration-issues)
5. [Phase 5: Report Generation Issues](#phase-5-report-generation-issues)
6. [Environment Issues](#environment-issues)
7. [CDK Import Execution Issues](#cdk-import-execution-issues)
8. [Performance Issues](#performance-issues)

## Phase 1: Resource Discovery Issues

### Issue: AWS Credentials Not Found

**Symptoms:**
```
❌ Environment validation failed:
   AWS CLI not configured. Run 'aws configure' first.
```

**Cause:** AWS CLI credentials not configured.

**Solutions:**

1. **Configure AWS CLI:**
   ```bash
   aws configure --profile <profile-name>
   ```

2. **Verify configuration:**
   ```bash
   aws sts get-caller-identity --profile <profile-name>
   ```

3. **Check credentials file:**
   ```bash
   cat ~/.aws/credentials
   cat ~/.aws/config
   ```

### Issue: Insufficient IAM Permissions

**Symptoms:**
```
[1/5] Discovering AWS resources...
❌ Phase 1 failed: Access Denied for lambda:ListFunctions
```

**Cause:** IAM user/role lacks necessary read permissions.

**Solutions:**

1. **Attach read-only policy:**
   ```bash
   aws iam attach-user-policy \
     --user-name <username> \
     --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
   ```

2. **Create custom minimal policy:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "lambda:List*",
           "lambda:Get*",
           "lambda:Describe*",
           "dynamodb:List*",
           "dynamodb:Describe*",
           "s3:List*",
           "s3:Get*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. **Test permissions:**
   ```bash
   aws lambda list-functions --profile <profile-name>
   ```

### Issue: No Resources Found

**Symptoms:**
```
[1/5] Discovering AWS resources...
✓ Found 0 Lambda functions
✓ Found 0 DynamoDB tables
```

**Cause:** Resources don't exist in specified region or filters are too restrictive.

**Solutions:**

1. **Verify resources exist:**
   ```bash
   aws lambda list-functions --region <region> --profile <profile>
   ```

2. **Check region:**
   - Ensure `--region` matches where resources are deployed
   - Resources may be in a different region

3. **Review filters:**
   - Remove or adjust `--resource-types` filter
   - Remove or adjust `--tag-filter`
   - Remove or adjust `--name-pattern`

4. **Run without filters:**
   ```bash
   python scripts/orchestrate.py \
     --profile <profile> \
     --region <region> \
     --output ./test
   ```

### Issue: Discovery Times Out

**Symptoms:**
```
[1/5] Discovering AWS resources...
❌ Phase 1 failed: Skill 'aws-resource-discovery' timed out after 10 minutes
```

**Cause:** Large number of resources takes longer than timeout.

**Solutions:**

1. **Increase timeout** in `skill_invoker.py`:
   ```python
   timeout=1800  # 30 minutes instead of 10
   ```

2. **Use resource type filters:**
   ```bash
   python scripts/orchestrate.py \
     --profile <profile> \
     --region <region> \
     --resource-types lambda,dynamodb \
     --output ./filtered
   ```

3. **Discover incrementally:**
   - First run: `--resource-types lambda`
   - Second run: `--resource-types dynamodb`
   - Merge results manually

### Issue: Invalid JSON in resources.json

**Symptoms:**
```
[2/5] Generating CDK constructs...
❌ Phase 2 failed: Invalid JSON in resources.json
```

**Cause:** Discovery phase wrote malformed JSON.

**Solutions:**

1. **Validate JSON:**
   ```bash
   python -m json.tool discovery/resources.json
   ```

2. **Check for encoding issues:**
   ```bash
   file discovery/resources.json
   ```

3. **Re-run discovery** with verbose mode:
   ```bash
   python scripts/orchestrate.py \
     --profile <profile> \
     --region <region> \
     --verbose \
     --output ./retry
   ```

## Phase 2: Code Generation Issues

### Issue: Unsupported Resource Type

**Symptoms:**
```
[2/5] Generating CDK constructs...
❌ Phase 2 failed: Unsupported resource type: elasticache
```

**Cause:** Resource type not yet supported by code generator.

**Solutions:**

1. **Check supported types** in `cdk-code-generator/README.md`

2. **Filter out unsupported types:**
   ```bash
   python scripts/orchestrate.py \
     --profile <profile> \
     --region <region> \
     --resource-types lambda,dynamodb,s3 \
     --output ./supported-only
   ```

3. **Generate manually** for unsupported types

4. **Request feature** in component skill issues

### Issue: Missing Required Resource Property

**Symptoms:**
```
[2/5] Generating CDK constructs...
❌ Phase 2 failed: Missing required property 'runtime' for Lambda function 'my-function'
```

**Cause:** Resource in AWS has incomplete configuration.

**Solutions:**

1. **Inspect resource:**
   ```bash
   aws lambda get-function \
     --function-name my-function \
     --profile <profile> \
     --region <region>
   ```

2. **Check resources.json:**
   ```bash
   cat discovery/resources.json | jq '.lambda[] | select(.name=="my-function")'
   ```

3. **Fix resource in AWS** if configuration is actually incomplete

4. **Skip problematic resource:**
   - Edit `discovery/resources.json`
   - Remove problematic resource
   - Re-run from Phase 2:
     ```bash
     python scripts/orchestrate.py --skip-phase 1 ...
     ```

### Issue: No Constructs Generated

**Symptoms:**
```
[2/5] Generating CDK constructs...
✓ Generated 0 construct files
```

**Cause:** resources.json is empty or malformed.

**Solutions:**

1. **Check resources.json:**
   ```bash
   cat discovery/resources.json
   ```

2. **Verify Phase 1 completed:**
   - Check for discovery output
   - Verify resource counts

3. **Re-run workflow** from Phase 1

### Issue: Invalid TypeScript Generated

**Symptoms:**
```
[3/5] Organizing into CDK stacks...
❌ Phase 3 failed: Invalid TypeScript syntax in generated constructs
```

**Cause:** Code generator produced malformed TypeScript.

**Solutions:**

1. **Check generated files:**
   ```bash
   cat cdk-generated/constructs/lambdas/*.ts
   ```

2. **Validate TypeScript:**
   ```bash
   cd cdk-generated/constructs
   tsc --noEmit *.ts
   ```

3. **Report issue** with:
   - Resource configuration from resources.json
   - Generated construct code
   - Error message

## Phase 3: Stack Organization Issues

### Issue: Invalid Stack Strategy

**Symptoms:**
```
[3/5] Organizing into CDK stacks...
❌ Phase 3 failed: Invalid stack strategy: 'region'
```

**Cause:** Specified strategy not supported.

**Solutions:**

1. **Use valid strategy:**
   - `layer` (default)
   - `service`
   - `tag`
   - `custom`

2. **Check spelling:**
   ```bash
   python scripts/orchestrate.py \
     --strategy layer \
     ...
   ```

### Issue: Missing Tag Key for Tag Strategy

**Symptoms:**
```
❌ Environment validation failed:
   --tag-key is required when using --strategy tag
```

**Cause:** Using tag strategy without specifying tag key.

**Solutions:**

1. **Add tag-key parameter:**
   ```bash
   python scripts/orchestrate.py \
     --strategy tag \
     --tag-key Application \
     ...
   ```

2. **Choose different strategy:**
   ```bash
   python scripts/orchestrate.py \
     --strategy layer \
     ...
   ```

### Issue: Custom Rules File Not Found

**Symptoms:**
```
❌ Environment validation failed:
   Custom rules file not found: ./my-rules.json
```

**Cause:** Path to custom rules file is incorrect.

**Solutions:**

1. **Verify file exists:**
   ```bash
   ls -la ./my-rules.json
   ```

2. **Use absolute path:**
   ```bash
   python scripts/orchestrate.py \
     --strategy custom \
     --custom-rules /full/path/to/my-rules.json \
     ...
   ```

3. **Validate JSON format:**
   ```bash
   python -m json.tool my-rules.json
   ```

### Issue: No Stacks Created

**Symptoms:**
```
[3/5] Organizing into CDK stacks...
✓ Created 0 stack files
```

**Cause:** No constructs found to organize.

**Solutions:**

1. **Verify Phase 2 output:**
   ```bash
   ls -la cdk-generated/constructs/
   ```

2. **Check for constructs:**
   ```bash
   find cdk-generated -name "*.ts"
   ```

3. **Re-run from Phase 2:**
   ```bash
   python scripts/orchestrate.py --skip-phase 1 ...
   ```

### Issue: TypeScript Compilation Errors

**Symptoms:**
```bash
cd cdk-organized
npm run build
# Error: Cannot find module 'constructs'
```

**Cause:** Dependencies not installed.

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd cdk-organized
   npm install
   ```

2. **Verify package.json:**
   ```bash
   cat package.json
   ```

3. **Clear and reinstall:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

## Phase 4: Import Configuration Issues

### Issue: Logical ID Extraction Failed

**Symptoms:**
```
[4/5] Generating import configurations...
❌ Phase 4 failed: Could not extract logical ID for resource 'my-function'
```

**Cause:** Stack file has non-standard construct instantiation pattern.

**Solutions:**

1. **Check stack file:**
   ```bash
   cat cdk-organized/lib/stacks/compute-stack.ts
   ```

2. **Verify construct pattern:**
   ```typescript
   new MyFunctionConstruct(this, 'MyFunction');  // Standard
   ```

3. **Manually create mapping:**
   - Edit `import-configs/mappings/<stack>-import.json`
   - Add missing mapping

### Issue: ARN Format Issues

**Symptoms:**
```
[4/5] Generating import configurations...
❌ Phase 4 failed: Invalid ARN format for resource 'my-function'
```

**Cause:** Resource ARN in resources.json is malformed.

**Solutions:**

1. **Check ARN in resources.json:**
   ```bash
   cat discovery/resources.json | jq '.lambda[] | .arn'
   ```

2. **Verify ARN format:**
   - Lambda: `arn:aws:lambda:region:account:function:name`
   - DynamoDB: `arn:aws:dynamodb:region:account:table/name`

3. **Fix in resources.json** and re-run Phase 4

### Issue: No Import Scripts Generated

**Symptoms:**
```
[4/5] Generating import configurations...
✓ Created import mappings for 25 resources
✓ Generated 0 import scripts
```

**Cause:** Script generation logic failed or no stacks found.

**Solutions:**

1. **Check mappings directory:**
   ```bash
   ls -la import-configs/mappings/
   ```

2. **Verify stacks exist:**
   ```bash
   ls -la cdk-organized/lib/stacks/
   ```

3. **Re-run Phase 4:**
   ```bash
   cd cdk-import-config-generator
   python scripts/generate_import_configs.py \
     --resources-file ../discovery/resources.json \
     --cdk-dir ../cdk-organized \
     --output-dir ../import-configs
   ```

## Phase 5: Report Generation Issues

### Issue: Report Template Not Found

**Symptoms:**
```
[5/5] Creating summary report...
⚠️  Report template not found, using minimal template
```

**Cause:** Assets file missing.

**Impact:** Minimal - falls back to basic template.

**Solutions:**

1. **Use generated report anyway** - it contains all necessary info

2. **Create custom template:**
   - Copy `assets/report-template.md` from another installation
   - Modify as needed

### Issue: Report Contains {{PLACEHOLDERS}}

**Symptoms:**
Report shows `{{RESOURCE_SUMMARY}}` instead of actual data.

**Cause:** Phase results not properly captured.

**Solutions:**

1. **Check phase_results** in workflow_engine.py

2. **Re-run workflow** with verbose mode

3. **Manually edit report** to add missing information

## Environment Issues

### Issue: Python Version Too Old

**Symptoms:**
```
SyntaxError: invalid syntax
  File "orchestrate.py", line 42
    def parse_arguments() -> argparse.Namespace:
```

**Cause:** Python version < 3.8.

**Solutions:**

1. **Check Python version:**
   ```bash
   python3 --version
   ```

2. **Upgrade Python:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.9

   # macOS
   brew install python@3.9
   ```

3. **Use specific Python version:**
   ```bash
   python3.9 scripts/orchestrate.py ...
   ```

### Issue: Missing Python Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'boto3'
```

**Cause:** Required Python packages not installed.

**Solutions:**

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Use virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

### Issue: Component Skill Not Found

**Symptoms:**
```
❌ Environment validation failed:
   Missing required component skills: cdk-code-generator
   Expected location: /path/to/aws-infra-skills
```

**Cause:** Component skill not installed or in wrong location.

**Solutions:**

1. **Verify skill locations:**
   ```bash
   ls -la aws-infra-skills/
   ```

2. **Expected structure:**
   ```
   aws-infra-skills/
   ├── aws-resource-discovery/
   ├── cdk-code-generator/
   ├── cdk-stack-organizer/
   ├── cdk-import-config-generator/
   └── aws-to-cdk-importer/
   ```

3. **Install missing skills**

### Issue: Output Directory Not Empty

**Symptoms:**
```
❌ Environment validation failed:
   Output directory already exists and is not empty: ./my-project
```

**Cause:** Trying to write to existing directory.

**Solutions:**

1. **Use different output directory:**
   ```bash
   python scripts/orchestrate.py --output ./my-project-v2 ...
   ```

2. **Remove existing directory:**
   ```bash
   rm -rf ./my-project
   ```

3. **Backup and remove:**
   ```bash
   mv ./my-project ./my-project.backup
   ```

## CDK Import Execution Issues

### Issue: CDK Not Installed

**Symptoms:**
```bash
./import-all.sh
bash: cdk: command not found
```

**Cause:** AWS CDK CLI not installed.

**Solutions:**

1. **Install CDK globally:**
   ```bash
   npm install -g aws-cdk
   ```

2. **Verify installation:**
   ```bash
   cdk --version
   ```

### Issue: Import Fails with "Resource Already Managed"

**Symptoms:**
```
cdk import ComputeStack
Error: Resource MyFunction is already managed by CloudFormation
```

**Cause:** Resource already part of another CloudFormation stack.

**Solutions:**

1. **Check existing stacks:**
   ```bash
   aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE
   ```

2. **Identify managing stack:**
   ```bash
   aws cloudformation describe-stack-resources \
     --stack-name <stack-name>
   ```

3. **Options:**
   - Remove resource from old stack first
   - Don't import this resource
   - Use CDK migrate instead of import

### Issue: Import Fails with "Resource Not Found"

**Symptoms:**
```
cdk import ComputeStack
Error: Resource with identifier arn:aws:lambda:...:my-function not found
```

**Cause:** Resource was deleted or ARN is incorrect.

**Solutions:**

1. **Verify resource exists:**
   ```bash
   aws lambda get-function --function-name my-function
   ```

2. **Check ARN in mapping file:**
   ```bash
   cat import-configs/mappings/compute-stack-import.json
   ```

3. **Update mapping** if ARN changed

4. **Remove from stack** if resource deleted

### Issue: CDK Diff Shows Changes After Import

**Symptoms:**
```bash
cdk diff ComputeStack
# Shows unexpected changes
```

**Cause:** Generated CDK code doesn't match actual AWS configuration.

**Solutions:**

1. **Review diff carefully:**
   ```bash
   cdk diff ComputeStack > diff.txt
   ```

2. **Expected for reference mode:**
   - Reference mode constructs don't manage full configuration
   - Some differences are normal

3. **Update construct code** to match AWS if needed

4. **Use full mode** if you need exact match:
   ```bash
   python scripts/orchestrate.py --mode full ...
   ```

## Performance Issues

### Issue: Workflow Very Slow

**Symptoms:**
Workflow takes much longer than expected.

**Causes & Solutions:**

1. **Large number of resources:**
   - Use `--resource-types` to filter
   - Import incrementally

2. **Slow network connection:**
   - Run from EC2 instance in same region
   - Use AWS CLI with endpoint URLs

3. **Verbose logging overhead:**
   - Remove `--verbose` flag
   - Only use for debugging

### Issue: High Memory Usage

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Causes & Solutions:**

1. **Too many resources at once:**
   - Filter by resource type
   - Import in batches

2. **Large resource configurations:**
   - Increase system memory
   - Use streaming JSON parser

### Issue: Disk Space Exhausted

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Causes & Solutions:**

1. **Check available space:**
   ```bash
   df -h
   ```

2. **Clean up:**
   ```bash
   # Remove old output directories
   rm -rf ./old-project
   ```

3. **Use different disk:**
   ```bash
   python scripts/orchestrate.py --output /mnt/larger-disk/my-project ...
   ```

## Getting Additional Help

If issues persist after trying these solutions:

1. **Check error.log:**
   ```bash
   cat <output-dir>/error.log
   ```

2. **Run with verbose mode:**
   ```bash
   python scripts/orchestrate.py --verbose ...
   ```

3. **Check component skill logs:**
   - Each skill may have additional logs
   - Check `<output-dir>/*/logs/`

4. **Report issue:**
   - Include error messages
   - Include relevant config files
   - Include output of `--dry-run --verbose`

5. **Review documentation:**
   - `references/workflow_guide.md`
   - `references/component_skills.md`
   - Component skill README files
