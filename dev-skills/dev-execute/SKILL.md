---
name: dev-execute
description: Execute specifications from configurable directory (defaults to ./.dev-docs/features/) in fresh sub-agent contexts. Two-phase workflow - Phase 1 implements and provides testing guidance, Phase 2 archives after user confirms testing complete. Supports single, parallel, and sequential execution.
---

<skill>

<overview>
  <purpose>Execute feature specifications from configured directory as delegated sub-tasks with fresh context</purpose>
  <benefit>Keeps main conversation clean while implementation happens in focused, isolated sub-agent contexts</benefit>
  <directory_config>Reads dev_docs_directory from root CLAUDE.md, defaults to ./.dev-docs/features/</directory_config>
  <two_phase_workflow>
    <phase name="implementation">
      <action>Sub-agent implements feature specification</action>
      <action>Provides suggested manual testing steps</action>
      <result>Feature stays in configured directory (NOT archived yet)</result>
    </phase>
    <phase name="completion">
      <action>User performs manual testing based on suggestions</action>
      <action>User explicitly confirms "feature X is complete" or "archive feature X"</action>
      <result>Feature archived to [configured_path]/completed/</result>
    </phase>
  </two_phase_workflow>
  <use_when>
    <case>Feature specifications have been created by dev-spec and are ready to implement</case>
    <case>User wants to execute one or more saved feature specifications</case>
    <case>Need to run multiple features in parallel or sequential order</case>
    <case>User has tested a feature and wants to mark it complete and archive it</case>
  </use_when>
</overview>

<tool_restrictions>
  <allowed_tools>
    <tool name="Task">Spawn sub-agents with subagent_type="general-purpose"</tool>
    <tool name="Read">Read feature specification files, read CLAUDE.md for configuration</tool>
    <tool name="Bash">Find files, create directories, archive specifications</tool>
    <tool name="Glob">Search for feature files by pattern</tool>
  </allowed_tools>
  <critical_pattern>
    <parallel_execution>ALL Task tool calls MUST be in a SINGLE message for parallel execution</parallel_execution>
  </critical_pattern>
</tool_restrictions>

<rules>
  <rule priority="critical">Read root CLAUDE.md for dev_docs_directory setting to determine spec directory (defaults to ./.dev-docs/features/ if not set)</rule>
  <rule priority="critical">NEVER archive features automatically after implementation - always wait for explicit user confirmation after manual testing</rule>
  <rule priority="critical">Sub-agents MUST provide suggested manual testing steps in their final report</rule>
  <rule priority="critical">All Task tool calls for parallel execution must be in a single message</rule>
  <rule priority="critical">For sequential execution, stop immediately on first failure</rule>
  <rule priority="high">Each sub-agent gets fresh context with only the specification content</rule>
  <rule priority="high">Verify configured directory exists before execution</rule>
  <rule priority="high">Create [configured_path]/completed/ directory if it doesn't exist</rule>
  <rule priority="high">When delegating to sub-agent, explicitly instruct them to provide manual testing steps</rule>
  <rule priority="medium">For parallel execution, report which features succeeded/failed separately</rule>
  <rule priority="medium">Archive format includes execution metadata (timestamp, status)</rule>
  <rule priority="medium">Clearly distinguish between "implemented" and "completed/tested" status</rule>
</rules>

<directory_configuration>
  <purpose>Determine where feature specifications are stored - reads configuration set by dev-spec</purpose>
  <workflow>
    <step name="read_claude_md">
      <action>Read root CLAUDE.md file (./CLAUDE.md)</action>
      <look_for>dev_docs_directory: [path]</look_for>
      <if_found>Use [path]/features/ for all specification reads</if_found>
      <if_not_found>Use default ./.dev-docs/features/</if_not_found>
    </step>
    <step name="use_configured_path">
      <action>Read specifications from [configured_path]/features/</action>
      <action>Archive completed specifications to [configured_path]/completed/</action>
    </step>
  </workflow>
  <important_notes>
    <note>This skill only READS the configuration - dev-spec is responsible for setting it</note>
    <note>Always check ROOT CLAUDE.md (./CLAUDE.md) - there may be multiple CLAUDE.md files in subdirectories</note>
    <note>The path is project-specific - different projects can have different paths</note>
    <note>If CLAUDE.md doesn't exist or doesn't have the setting, default to ./.dev-docs/features/</note>
  </important_notes>
</directory_configuration>

<execution_modes>
  <mode name="implement_single">
    <when>User requests to implement/execute one feature by number, name, or "latest"</when>
    <workflow>
      <step>Resolve feature file using matching strategy</step>
      <step>Read complete specification content</step>
      <step>Delegate to sub-agent via Task tool with instruction to provide testing steps</step>
      <step>Wait for completion</step>
      <step>Present implementation results and manual testing suggestions to user</step>
      <step>Feature remains in ./.dev-docs/features/ awaiting testing confirmation</step>
    </workflow>
    <no_automatic_archiving>Feature stays in features/ directory until user confirms completion</no_automatic_archiving>
  </mode>

  <mode name="implement_parallel">
    <when>Features are independent with no shared files or dependencies</when>
    <when>User explicitly requests parallel execution</when>
    <workflow>
      <step>Read all requested feature specifications</step>
      <step>Spawn ALL Task tools simultaneously in one message, each instructed to provide testing steps</step>
      <step>Wait for all sub-agents to complete</step>
      <step>Present consolidated implementation results and testing suggestions for each feature</step>
      <step>Features remain in ./.dev-docs/features/ awaiting testing confirmation</step>
    </workflow>
    <constraint>Maximum efficiency but requires feature independence</constraint>
    <critical>All Task calls must be in ONE message</critical>
    <no_automatic_archiving>Features stay in features/ directory until user confirms completion</no_automatic_archiving>
  </mode>

  <mode name="implement_sequential">
    <when>Features have dependencies or modify shared files</when>
    <when>Order matters for correctness</when>
    <when>Execution strategy not specified (default for safety)</when>
    <workflow>
      <step>Execute features one at a time in order, each instructed to provide testing steps</step>
      <step>Wait for each completion before starting next</step>
      <step>Stop immediately on first failure</step>
      <step>Present implementation results and testing suggestions after each feature</step>
      <step>Features remain in ./.dev-docs/features/ awaiting testing confirmation</step>
    </workflow>
    <no_automatic_archiving>Features stay in features/ directory until user confirms completion</no_automatic_archiving>
  </mode>

  <mode name="complete_and_archive">
    <when>User explicitly confirms feature is tested and ready to archive</when>
    <when>User says "feature X is complete", "archive feature X", "mark feature X done"</when>
    <workflow>
      <step>Resolve feature file in ./.dev-docs/features/</step>
      <step>Verify feature file exists (not already archived)</step>
      <step>Add completion metadata (timestamp, status)</step>
      <step>Move to ./.dev-docs/features/completed/</step>
      <step>Confirm archival to user</step>
    </workflow>
    <trigger_phrases>
      <phrase>feature X is complete</phrase>
      <phrase>archive feature X</phrase>
      <phrase>mark feature X done</phrase>
      <phrase>complete feature X</phrase>
    </trigger_phrases>
  </mode>
</execution_modes>

<manual_testing_guidance>
  <requirement>All sub-agents MUST include suggested manual testing steps in their final report</requirement>
  <sub_agent_instruction>
    When delegating to sub-agent, include this instruction in the prompt:
    "After implementing the feature, provide a section called 'Suggested Manual Testing Steps' with specific, actionable steps the user should perform to verify the feature works correctly."
  </sub_agent_instruction>
  <testing_step_quality>
    <good>Test user login with valid credentials at http://localhost:3000/login</good>
    <good>Verify API endpoint returns 200 status: curl http://localhost:8080/api/users</good>
    <good>Check database has new table: SELECT * FROM user_sessions;</good>
    <bad>Test the feature</bad>
    <bad>Make sure it works</bad>
  </testing_step_quality>
  <presentation>
    After sub-agent completes, present testing steps clearly to user and remind them to confirm completion after testing
  </presentation>
</manual_testing_guidance>

<feature_resolution>
  <strategy name="by_number">
    <pattern>Match zero-padded numbers (5 matches 005-*.md)</pattern>
    <location>[configured_path]/features/</location>
  </strategy>
  <strategy name="by_name">
    <pattern>Find files containing name string in filename</pattern>
    <example>auth matches 005-user-authentication.md</example>
  </strategy>
  <strategy name="most_recent">
    <command>ls -t [configured_path]/features/*.md | head -1</command>
  </strategy>
  <conflict_resolution>
    <one_match>Use that file</one_match>
    <multiple_matches>List options and ask user to choose</multiple_matches>
    <no_matches>Report error and list available features</no_matches>
  </conflict_resolution>
  <note>configured_path comes from dev_docs_directory in root CLAUDE.md, defaults to ./.dev-docs</note>
</feature_resolution>

<archiving>
  <destination>[configured_path]/completed/</destination>
  <format>
    <filename>[number]-[name].md</filename>
    <metadata>
      <field>executed: [ISO timestamp of implementation]</field>
      <field>completed: [ISO timestamp of archival]</field>
      <field>status: completed</field>
    </metadata>
  </format>
  <timing>Only after user explicitly confirms manual testing is complete</timing>
  <trigger>User must say "feature X is complete" or similar confirmation phrase</trigger>
  <note>configured_path comes from dev_docs_directory in root CLAUDE.md, defaults to ./.dev-docs</note>
</archiving>

<error_handling>
  <scenario type="feature_fails_implementation">
    <single>Report failure with error details, do not archive, feature stays in features/</single>
    <parallel>Report which succeeded/failed, do not archive any, all stay in features/</parallel>
    <sequential>Stop immediately, do not execute remaining features, failed feature stays in features/</sequential>
  </scenario>
  <scenario type="file_not_found">
    <action>List available features in [configured_path]/features/</action>
    <action>Ask user to clarify which feature to execute</action>
  </scenario>
  <scenario type="multiple_matches">
    <action>List all matching feature files</action>
    <action>Ask user to specify by full number or more specific name</action>
  </scenario>
  <scenario type="already_archived">
    <when>User tries to complete/archive a feature that's already in completed/</when>
    <action>Inform user the feature is already archived</action>
    <action>Show location in [configured_path]/completed/</action>
  </scenario>
</error_handling>

<examples>
  <example name="implement_single_feature">
    <user_request>Execute feature 005</user_request>
    <agent_action>
      <step>Find [configured_path]/features/005-user-authentication.md</step>
      <step>Read specification</step>
      <step>Spawn Task tool with specification + instruction to provide testing steps</step>
      <step>Wait for sub-agent completion</step>
      <step>Present implementation results + suggested manual testing steps</step>
      <step>Remind user: "Feature 005 has been implemented. Please test using the steps above, then confirm completion when ready."</step>
      <step>Feature remains in [configured_path]/features/005-user-authentication.md</step>
    </agent_action>
  </example>

  <example name="complete_tested_feature">
    <user_request>Feature 005 is complete</user_request>
    <agent_action>
      <step>Find [configured_path]/features/005-user-authentication.md</step>
      <step>Add completion metadata (executed timestamp, completed timestamp, status)</step>
      <step>Move to [configured_path]/completed/005-user-authentication.md</step>
      <step>Confirm: "Feature 005 archived to [configured_path]/completed/"</step>
    </agent_action>
  </example>

  <example name="implement_parallel_features">
    <user_request>Execute features 005, 006, and 007 in parallel</user_request>
    <agent_action>
      <step>Read all three feature specifications</step>
      <step>Spawn three Task tools in single message, each instructed to provide testing steps</step>
      <step>Wait for all completions</step>
      <step>Present consolidated results with testing steps for each feature</step>
      <step>Remind user: "All three features implemented. Please test each one, then confirm completion individually or together."</step>
      <step>All three features remain in [configured_path]/features/</step>
    </agent_action>
    <critical>All Task calls must be in ONE message</critical>
  </example>

  <example name="complete_multiple_tested_features">
    <user_request>Features 005, 006, and 007 are all complete</user_request>
    <agent_action>
      <step>Archive 005-user-authentication.md to completed/</step>
      <step>Archive 006-api-endpoints.md to completed/</step>
      <step>Archive 007-ui-components.md to completed/</step>
      <step>Confirm: "All three features archived to [configured_path]/completed/"</step>
    </agent_action>
  </example>

  <example name="sequential_with_implementation_failure">
    <user_request>Execute features 005, 006, 007 sequentially</user_request>
    <scenario>Feature 006 fails during implementation</scenario>
    <agent_action>
      <step>Execute feature 005 successfully, provide testing steps</step>
      <step>005 remains in [configured_path]/features/ awaiting testing</step>
      <step>Execute feature 006, encounters error</step>
      <step>Stop execution, do not run feature 007</step>
      <step>Report failure at feature 006, no archival, both 005 and 006 stay in features/</step>
    </agent_action>
  </example>

  <example name="user_testing_flow">
    <conversation>
      <user>Execute feature 005</user>
      <agent>Implementation complete. Suggested manual testing steps:
        1. Start the application: npm run dev
        2. Navigate to http://localhost:3000/login
        3. Enter test credentials: user@example.com / password123
        4. Verify successful login and redirect to dashboard

        Feature 005 has been implemented. Please test using the steps above, then let me know when it's complete.</agent>
      <user>*user tests the feature*</user>
      <user>Feature 005 is complete</user>
      <agent>Feature 005 has been archived to [configured_path]/completed/005-user-authentication.md</agent>
    </conversation>
  </example>
</examples>

<related_skills>
  <skill name="dev-orchestrator">Orchestrator for overall feature development workflow</skill>
  <skill name="dev-spec">Creates feature specifications that this skill executes</skill>
  <skill name="task-creator">For simpler tasks rather than complex features</skill>
</related_skills>

</skill>
