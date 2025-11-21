---
name: dev-orchestrator
description: Orchestrates systematic development workflow for any software development task - from simple bug fixes to complex multi-file features. Separates specification from implementation, provides testing guidance, and manages completion workflow. Use when user requests to implement, build, develop, or fix any code.
---

<skill>

<overview>
  <purpose>Orchestrates systematic workflow for all software development by separating specification from implementation</purpose>
  <benefit>Keeps main context clean for requirements gathering while implementation happens in focused, isolated sub-agent contexts</benefit>
  <use_when>
    <case>User requests to implement, build, develop, or create new functionality</case>
    <case>User requests to fix bugs or issues</case>
    <case>Task requires any code changes (simple or complex)</case>
    <case>User wants systematic approach with testing guidance</case>
    <case>Task involves multiple files or architectural decisions</case>
  </use_when>
  <workflow_phases>
    <phase name="specification">Clarify requirements and generate structured spec</phase>
    <phase name="implementation">Execute spec in clean sub-agent context</phase>
    <phase name="testing">User performs manual testing with provided guidance</phase>
    <phase name="completion">User confirms and feature is archived</phase>
  </workflow_phases>
</overview>

<tool_restrictions>
  <allowed_tools>
    <tool name="Skill">Invoke dev-spec and dev-execute skills</tool>
    <tool name="AskUserQuestion">Clarify requirements before specification</tool>
  </allowed_tools>
  <forbidden_tools>
    <tool name="Task">Do not spawn sub-agents directly - use dev-execute skill instead</tool>
    <tool name="Read">Do not read specifications - let dev-execute handle that</tool>
    <tool name="Write">Do not create specifications directly - use dev-spec skill instead</tool>
  </forbidden_tools>
  <orchestrator_role>This is a GUIDANCE skill that instructs Claude to invoke other skills at appropriate times</orchestrator_role>
</tool_restrictions>

<rules>
  <rule priority="critical">This is an ORCHESTRATOR skill - provide guidance and invoke dev-spec and dev-execute, do not implement directly</rule>
  <rule priority="critical">Always use dev-spec to create specifications before implementation</rule>
  <rule priority="critical">Always use dev-execute to execute specifications, never implement in main context</rule>
  <rule priority="critical">Never archive features automatically - dev-execute handles two-phase workflow (implementation then user confirmation)</rule>
  <rule priority="high">After dev-execute completes implementation and provides testing steps, remind user to test before marking complete</rule>
  <rule priority="high">When user confirms "feature X is complete", invoke dev-execute in completion mode to archive</rule>
  <rule priority="high">For multiple related changes, discuss parallel vs sequential execution with user</rule>
  <rule priority="medium">Adapt specification complexity to task complexity (dev-spec handles this)</rule>
  <rule priority="medium">Features stay in ./.dev-docs/features/ until user confirms testing complete</rule>
</rules>

<complete_workflow>
  <phase_1 name="specification">
    <tool>dev-spec skill</tool>
    <actions>
      <action>Clarify requirements with user through targeted questions</action>
      <action>Ask about architecture, patterns, constraints, success criteria</action>
      <action>Generate XML-structured specification with implementation guidance</action>
      <action>Save to ./.dev-docs/features/[number]-[name].md</action>
      <action>Ask user: "Ready to execute this specification?"</action>
    </actions>
    <note>dev-spec automatically adjusts depth based on task complexity</note>
  </phase_1>

  <phase_2 name="implementation">
    <trigger>User confirms ready to execute specification</trigger>
    <tool>dev-execute skill</tool>
    <actions>
      <action>Invoke dev-execute with feature number or name</action>
      <action>dev-execute reads specification from ./.dev-docs/features/</action>
      <action>Spawns sub-agent in clean context with specification as prompt</action>
      <action>Sub-agent implements and provides suggested manual testing steps</action>
      <action>Feature remains in ./.dev-docs/features/ (NOT archived yet)</action>
    </actions>
    <execution_strategies>
      <strategy name="single">One specification, focused implementation</strategy>
      <strategy name="parallel">Multiple independent specs with no shared files</strategy>
      <strategy name="sequential">Multiple dependent specs that must run in order</strategy>
    </execution_strategies>
  </phase_2>

  <phase_3 name="testing">
    <trigger>dev-execute completes implementation and provides testing steps</trigger>
    <actions>
      <action>Present testing suggestions from sub-agent to user</action>
      <action>Remind user: "Feature X has been implemented. Please test using the steps above, then confirm completion when ready."</action>
      <action>Wait for user to perform manual testing</action>
      <action>Feature stays in ./.dev-docs/features/ during testing</action>
    </actions>
    <important>Do NOT automatically archive or mark complete - wait for explicit user confirmation</important>
  </phase_3>

  <phase_4 name="completion">
    <trigger>User explicitly confirms: "feature X is complete", "archive feature X", "mark feature X done"</trigger>
    <actions>
      <action>Invoke dev-execute in completion mode</action>
      <action>dev-execute adds completion metadata and archives to ./.dev-docs/features/completed/</action>
      <action>Confirm to user: "Feature X archived to completed/"</action>
    </actions>
  </phase_4>
</complete_workflow>

<integration_with_dev_feature>
  <two_phase_workflow>
    <phase name="implementation">
      <what_happens>Sub-agent implements code and provides testing steps</what_happens>
      <result>Feature stays in ./.dev-docs/features/ awaiting testing</result>
      <no_automatic_archiving>Feature is implemented but not yet marked complete</no_automatic_archiving>
    </phase>
    <phase name="completion">
      <trigger>User confirms testing complete</trigger>
      <what_happens>dev-execute archives to ./.dev-docs/features/completed/</what_happens>
      <result>Feature marked complete with metadata (executed timestamp, completed timestamp)</result>
    </phase>
  </two_phase_workflow>
  <testing_phase_guidance>
    <after_implementation>Always remind user to test before marking complete</after_implementation>
    <testing_steps>Sub-agent provides specific, actionable testing steps</testing_steps>
    <user_control>User decides when testing is complete and feature is ready to archive</user_control>
  </testing_phase_guidance>
  <completion_triggers>
    <phrase>feature X is complete</phrase>
    <phrase>archive feature X</phrase>
    <phrase>mark feature X done</phrase>
    <phrase>complete feature X</phrase>
  </completion_triggers>
</integration_with_dev_feature>

<skill_integration>
  <relationship>
    <orchestrator>feature-creator (this skill) - provides workflow guidance</orchestrator>
    <specification>dev-spec - creates executable specifications</specification>
    <execution>dev-execute - implements specifications in sub-agents</execution>
  </relationship>
  <communication_flow>
    <step>User requests development work</step>
    <step>feature-creator invokes dev-spec</step>
    <step>dev-spec clarifies requirements and creates specification</step>
    <step>dev-spec saves to ./.dev-docs/features/</step>
    <step>dev-spec asks user: "Execute now?"</step>
    <step>If yes, feature-creator invokes dev-execute</step>
    <step>dev-execute spawns sub-agent and implements</step>
    <step>Sub-agent provides testing steps, feature stays in ./.dev-docs/features/</step>
    <step>feature-creator reminds user to test</step>
    <step>User tests and confirms: "feature X is complete"</step>
    <step>feature-creator invokes dev-execute in completion mode</step>
    <step>dev-execute archives to ./.dev-docs/features/completed/</step>
  </communication_flow>
</skill_integration>

<complexity_handling>
  <simple_work>
    <examples>Bug fixes, single-file changes, small enhancements</examples>
    <behavior>dev-spec generates lightweight specification</behavior>
    <result>Quick, focused implementation with minimal overhead</result>
  </simple_work>
  <complex_work>
    <examples>Multi-file features, architectural changes, new components</examples>
    <behavior>dev-spec generates comprehensive specification with extended thinking</behavior>
    <result>Thorough planning ensures quality implementation</result>
  </complex_work>
  <adaptive>dev-spec automatically adjusts depth based on task complexity signals</adaptive>
</complexity_handling>

<benefits>
  <benefit type="separation_of_concerns">
    <description>Main context stays clean for requirements gathering and planning</description>
    <description>Implementation happens in fresh context with only the specification</description>
    <description>No pollution from exploration mixed with execution</description>
  </benefit>
  <benefit type="quality">
    <description>Systematic thinking produces comprehensive specifications</description>
    <description>Clear success criteria ensure completion signals</description>
    <description>Testing guidance built into every implementation</description>
    <description>Two-phase workflow prevents premature completion</description>
  </benefit>
  <benefit type="reusability">
    <description>Specifications saved as reviewable markdown files</description>
    <description>Can edit and rerun specifications</description>
    <description>Archive completed work for reference</description>
  </benefit>
  <benefit type="scalability">
    <description>Parallel execution for independent components</description>
    <description>Sequential execution for dependent tasks</description>
    <description>No token concerns with Claude Max</description>
  </benefit>
</benefits>

<error_handling>
  <scenario type="spec_feature_failure">
    <when>dev-spec cannot create specification</when>
    <action>Ask user for more details about requirements</action>
    <action>Retry specification with additional context</action>
  </scenario>

  <scenario type="implementation_failure">
    <when>dev-execute reports implementation errors</when>
    <action>Feature stays in ./.dev-docs/features/ (not archived)</action>
    <action>Review error details with user</action>
    <action>May need to revise specification and re-execute</action>
  </scenario>

  <scenario type="testing_reveals_issues">
    <when>User tests and finds problems</when>
    <action>Do not archive current feature</action>
    <action>Option 1: Create new specification for fixes and execute</action>
    <action>Option 2: Revise original specification and re-execute</action>
    <action>Archive only after user confirms everything works</action>
  </scenario>

  <scenario type="user_requests_changes_after_implementation">
    <when>User wants to modify feature after seeing results</when>
    <action>Do not archive current feature</action>
    <action>Create new specification for modifications</action>
    <action>Execute modification specification</action>
    <action>User tests combined result, then confirms completion</action>
  </scenario>
</error_handling>

<orchestrator_behavior>
  <automation_level>
    <when_invoked>Automatically invoke dev-spec for specification phase</when_invoked>
    <after_spec>Ask user if ready to execute, then invoke dev-execute if confirmed</after_spec>
    <after_implementation>Remind user to test, wait for confirmation before archiving</after_implementation>
    <on_completion_trigger>Invoke dev-execute in completion mode to archive</on_completion_trigger>
  </automation_level>
  <user_control>
    <choice>User can review/edit specification before execution</choice>
    <choice>User controls when to execute</choice>
    <choice>User controls testing timeline</choice>
    <choice>User explicitly confirms completion before archival</choice>
  </user_control>
</orchestrator_behavior>

<examples>
  <example name="simple_bug_fix">
    <user_request>Fix the login button that's not responding on mobile</user_request>
    <workflow>
      <step phase="specification">
        <action>feature-creator invokes dev-spec</action>
        <action>dev-spec asks: "What's the expected behavior? Any specific mobile devices affected?"</action>
        <action>Generates lightweight specification (simple fix)</action>
        <action>Saves to ./.dev-docs/features/001-fix-login-button.md</action>
      </step>
      <step phase="implementation">
        <action>User confirms: "Execute now"</action>
        <action>feature-creator invokes dev-execute</action>
        <action>Sub-agent fixes button, provides testing steps: "Test on iOS Safari and Android Chrome"</action>
        <result>Feature stays in ./.dev-docs/features/001-fix-login-button.md</result>
      </step>
      <step phase="testing">
        <action>User tests on mobile devices</action>
        <action>Verifies button works correctly</action>
      </step>
      <step phase="completion">
        <action>User confirms: "Feature 001 is complete"</action>
        <action>feature-creator invokes dev-execute in completion mode</action>
        <result>Feature archived to ./.dev-docs/features/completed/001-fix-login-button.md</result>
      </step>
    </workflow>
  </example>

  <example name="complex_feature">
    <user_request>Build a user authentication system with OAuth support</user_request>
    <workflow>
      <step phase="specification">
        <action>feature-creator invokes dev-spec</action>
        <action>dev-spec asks: "OAuth providers? Token storage? Session management?"</action>
        <action>Generates comprehensive specification with architecture details</action>
        <action>Saves to ./.dev-docs/features/002-user-authentication.md</action>
      </step>
      <step phase="implementation">
        <action>User confirms: "Execute now"</action>
        <action>feature-creator invokes dev-execute</action>
        <action>Sub-agent implements OAuth flow, provides detailed testing steps</action>
        <result>Feature stays in ./.dev-docs/features/002-user-authentication.md</result>
      </step>
      <step phase="testing">
        <action>User tests OAuth flow with different providers</action>
        <action>Verifies token storage and session management</action>
        <action>Finds issue with token refresh</action>
      </step>
      <step phase="iteration">
        <action>User: "Token refresh isn't working"</action>
        <action>feature-creator invokes dev-spec for fix</action>
        <action>Creates 003-fix-token-refresh.md</action>
        <action>Executes fix, user tests again</action>
      </step>
      <step phase="completion">
        <action>User confirms: "Features 002 and 003 are complete"</action>
        <action>feature-creator invokes dev-execute for both</action>
        <result>Both archived to ./.dev-docs/features/completed/</result>
      </step>
    </workflow>
  </example>

  <example name="parallel_execution">
    <user_request>Build separate auth, API, and UI components in parallel</user_request>
    <workflow>
      <step phase="specification">
        <action>feature-creator invokes dev-spec</action>
        <action>dev-spec creates 3 independent specifications</action>
        <action>Saves as 004-auth.md, 005-api.md, 006-ui.md</action>
      </step>
      <step phase="implementation">
        <action>User confirms: "Execute all in parallel"</action>
        <action>feature-creator invokes dev-execute: "Execute features 004, 005, 006 in parallel"</action>
        <action>dev-execute spawns 3 sub-agents simultaneously (one message)</action>
        <action>All 3 provide testing steps, remain in ./.dev-docs/features/</action>
      </step>
      <step phase="testing">
        <action>User tests auth component - works</action>
        <action>User tests API component - works</action>
        <action>User tests UI component - has bug</action>
      </step>
      <step phase="partial_completion">
        <action>User: "Features 004 and 005 are complete"</action>
        <action>feature-creator archives 004 and 005, leaves 006 for fixing</action>
      </step>
      <step phase="fix_and_complete">
        <action>Create 007-fix-ui-bug.md, execute, test</action>
        <action>User: "Features 006 and 007 are complete"</action>
        <action>Archive both to completed/</action>
      </step>
    </workflow>
  </example>

  <example name="sequential_execution">
    <user_request>Set up database, create migrations, then seed data (must be in order)</user_request>
    <workflow>
      <step phase="specification">
        <action>dev-spec creates 3 specifications in sequence</action>
        <action>008-setup-database.md, 009-create-migrations.md, 010-seed-data.md</action>
      </step>
      <step phase="implementation">
        <action>User: "Execute sequentially"</action>
        <action>dev-execute executes 008, waits for completion, provides testing</action>
        <action>User tests database setup: "Feature 008 is complete"</action>
        <action>dev-execute archives 008, executes 009, provides testing</action>
        <action>User tests migrations: "Feature 009 is complete"</action>
        <action>dev-execute archives 009, executes 010, provides testing</action>
        <action>User tests seed data: "Feature 010 is complete"</action>
        <action>dev-execute archives 010</action>
      </step>
    </workflow>
    <note>Sequential execution allows testing between dependent steps</note>
  </example>

  <example name="user_conversation_flow">
    <conversation>
      <user>I need to add dark mode support to the app</user>
      <agent>I'll orchestrate the development workflow. First, let me invoke dev-spec to create a specification.</agent>
      <agent>*invokes dev-spec*</agent>
      <agent>dev-spec is working on the specification...</agent>
      <agent>Specification created and saved to ./.dev-docs/features/011-dark-mode.md. Ready to execute?</agent>
      <user>Yes</user>
      <agent>*invokes dev-execute*</agent>
      <agent>Implementation complete! Suggested manual testing steps:
        1. Toggle dark mode in settings
        2. Verify all pages render correctly in dark mode
        3. Check color contrast meets accessibility standards

        Feature 011 has been implemented. Please test using the steps above, then let me know when it's complete.</agent>
      <user>*user tests*</user>
      <user>Everything looks good. Feature 011 is complete.</user>
      <agent>*invokes dev-execute in completion mode*</agent>
      <agent>Feature 011 has been archived to ./.dev-docs/features/completed/011-dark-mode.md</agent>
    </conversation>
  </example>
</examples>

<related_skills>
  <skill name="dev-spec">Creates XML-structured feature specifications with adaptive complexity</skill>
  <skill name="dev-execute">Executes specifications in sub-agents with two-phase testing workflow</skill>
</related_skills>

</skill>
