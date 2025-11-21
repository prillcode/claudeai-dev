---
name: dev-spec
description: Expert prompt engineer that creates optimized, XML-structured specifications for all software development tasks. Adapts specification depth based on task complexity - lightweight for simple bugs, comprehensive for complex features. Includes testing step generation guidance. Saves specifications to configurable directory (defaults to ./.dev-docs/features/).
---

<skill>

<overview>
  <purpose>Creates optimized, XML-structured specifications for all software development tasks</purpose>
  <benefit>Transforms vague requests into comprehensive, executable specifications through systematic analysis and clarification</benefit>
  <adaptive>Adjusts specification depth based on task complexity - lightweight for simple bugs, comprehensive for complex features</adaptive>
  <testing_integration>All specifications instruct implementers to provide suggested manual testing steps</testing_integration>
</overview>

<when_to_use>
  <case>Creating specifications for ANY development work (spec-feature adapts depth automatically)</case>
  <case>Simple bug fixes requiring minimal planning</case>
  <case>Single-file changes or small enhancements</case>
  <case>Multi-file features requiring architectural decisions</case>
  <case>Complex features needing comprehensive planning</case>
  <case>User requests development with incomplete details</case>
  <case>Working with complex requirements needing clarification</case>
</when_to_use>

<tool_restrictions>
  <allowed_tools>
    <tool name="Read">Read existing feature files to determine numbering, read CLAUDE.md for configuration</tool>
    <tool name="Write">Save generated specifications to configured directory, update CLAUDE.md with directory setting</tool>
    <tool name="Bash">Create directories, list files for numbering</tool>
    <tool name="Glob">Find existing feature files</tool>
    <tool name="AskUserQuestion">Clarify requirements before specification, ask about directory configuration</tool>
  </allowed_tools>
  <forbidden_tools>
    <tool name="Task">Do not spawn sub-agents - dev-execute handles execution</tool>
    <tool name="Edit">Always write complete specifications, never edit existing ones</tool>
  </forbidden_tools>
  <specification_role>This skill creates specifications only - never implements features directly</specification_role>
</tool_restrictions>

<rules>
  <rule priority="critical">Before first use, check root CLAUDE.md for dev_docs_directory setting - if not found, prompt user and save their choice</rule>
  <rule priority="critical">Always clarify ambiguous requirements before generating specifications</rule>
  <rule priority="critical">Save all specifications to configured directory (check CLAUDE.md for dev_docs_directory, default to ./.dev-docs/features/)</rule>
  <rule priority="critical">Include testing step generation guidance in every specification</rule>
  <rule priority="critical">Specifications are used for ALL development work (simple bugs to complex features)</rule>
  <rule priority="critical">Every specification MUST instruct implementer to provide "Suggested Manual Testing Steps" after implementation</rule>
  <rule priority="high">Test Golden Rule: Would a colleague with minimal context understand this request?</rule>
  <rule priority="high">Include WHY explanations for constraints, not just WHAT</rule>
  <rule priority="high">Always reference CLAUDE.md for project conventions</rule>
  <rule priority="high">Include verification and success criteria in every specification</rule>
  <rule priority="high">Adapt specification depth based on task complexity signals</rule>
  <rule priority="medium">Use numbered file format: 001-feature-name.md</rule>
  <rule priority="medium">Ask user if ready to execute after saving specification</rule>
</rules>

<adaptive_complexity>
  <simple_task>
    <signals>Single file, bug fix, clear goal, obvious solution</signals>
    <specification_style>Lightweight - objective, context, requirements, implementation, verification only</specification_style>
    <omit>Extended thinking triggers, research sections, "go beyond basics" language</omit>
    <example_tasks>Fix button styling, update text content, correct validation logic</example_tasks>
  </simple_task>
  <moderate_task>
    <signals>Multiple files, some design decisions, moderate complexity</signals>
    <specification_style>Standard - full XML structure with clear implementation guidance</specification_style>
    <include>Context, requirements, implementation approach, verification steps</include>
    <example_tasks>Add new API endpoint, create component with state, implement form validation</example_tasks>
  </moderate_task>
  <complex_task>
    <signals>Multi-file, architectural decisions, research needed, multiple approaches</signals>
    <specification_style>Comprehensive - full XML structure with research, extended thinking, parallel tool calling</specification_style>
    <include>Extended thinking triggers, WHY explanations, parallel tool calling guidance, thorough verification</include>
    <example_tasks>Authentication system, database schema changes, new feature with integrations</example_tasks>
  </complex_task>
  <assessment>Analyze task complexity before generating specification and adjust depth accordingly</assessment>
</adaptive_complexity>

<testing_guidance>
  <requirement>Every specification MUST instruct the implementer to provide suggested manual testing steps</requirement>
  <specification_pattern>
    Include this in the verification section of every specification:

    "After implementing this feature, provide a 'Suggested Manual Testing Steps' section with specific, actionable steps for the user to verify the feature works correctly."
  </specification_pattern>
  <testing_step_quality>
    <good>Start dev server with npm run dev, then navigate to http://localhost:3000/login</good>
    <good>Test API endpoint: curl http://localhost:8080/api/users | jq</good>
    <good>Verify database table created: SELECT * FROM user_sessions;</good>
    <bad>Test the feature</bad>
    <bad>Make sure it works</bad>
  </testing_step_quality>
  <importance>Testing steps critical for dev-execute two-phase workflow (implementation → testing → completion)</importance>
</testing_guidance>

<directory_configuration>
  <purpose>Determine where to save development specifications - configurable per project</purpose>
  <workflow>
    <step name="check_claude_md">
      <action>Read root CLAUDE.md file (./CLAUDE.md)</action>
      <look_for>dev_docs_directory: [path]</look_for>
      <if_found>Use that path for all specification saves/reads</if_found>
      <if_not_found>Proceed to prompt user</if_not_found>
    </step>
    <step name="prompt_user">
      <when>dev_docs_directory not found in root CLAUDE.md</when>
      <message>
        Where should I save development specifications?

        1. ./.dev-docs (recommended default)
        2. Custom path (you specify)

        Your choice will be saved to the root CLAUDE.md so you won't be asked again for this project.

        Choose (1-2):
      </message>
      <if_option_1>Use ./.dev-docs/features/ as the path</if_option_1>
      <if_option_2>Ask: "Enter the path (e.g., ./docs/features or ./planning/specs):"</if_option_2>
    </step>
    <step name="save_to_claude_md">
      <action>Add or update dev_docs_directory setting in root CLAUDE.md</action>
      <format>
        ## Development Workflow

        dev_docs_directory: [user's choice]/features
      </format>
      <note>If CLAUDE.md doesn't exist, create it with this setting</note>
      <note>Always save to ROOT CLAUDE.md (./CLAUDE.md), not subdirectories</note>
    </step>
    <step name="create_directory">
      <action>Create the configured directory if it doesn't exist</action>
      <command>mkdir -p [configured_path]/features</command>
    </step>
  </workflow>
  <usage_pattern>
    <first_time>Check CLAUDE.md → Prompt if needed → Save choice → Use path</first_time>
    <subsequent>Read CLAUDE.md → Use path silently</subsequent>
  </usage_pattern>
  <important_notes>
    <note>Always check ROOT CLAUDE.md (./CLAUDE.md) - there may be multiple CLAUDE.md files in subdirectories</note>
    <note>The path is project-specific - different projects can have different paths</note>
    <note>If user doesn't specify, default is ./.dev-docs/features/</note>
    <note>This configuration is shared between spec-feature and dev-execute skills</note>
  </important_notes>
</directory_configuration>

<specification_process>
  <step name="analyze">
    <clarity_check>
      <question>Would a colleague with minimal context understand what's being asked?</question>
      <look_for>
        <ambiguity>Ambiguous terms that could mean multiple things</ambiguity>
        <examples>Missing examples that would clarify desired outcome</examples>
        <constraints>Missing details about constraints or requirements</constraints>
        <context>Unclear context (what it's for, who it's for, why it matters)</context>
      </look_for>
    </clarity_check>
    <complexity_assessment>
      <simple>Single file, clear goal, obvious solution</simple>
      <moderate>Multiple files, some design decisions</moderate>
      <complex>Multi-file, research needed, architectural decisions, multiple approaches</complex>
    </complexity_assessment>
    <execution_strategy>
      <single>Task has clear dependencies, single cohesive goal, sequential steps</single>
      <multiple_parallel>Sub-tasks independent, no shared files, can run simultaneously</multiple_parallel>
      <multiple_sequential>Sub-tasks have dependencies, one must finish before next starts</multiple_sequential>
    </execution_strategy>
    <reasoning_depth>
      <simple>Standard specification without extended thinking triggers</simple>
      <complex>Include extended thinking triggers for complex reasoning, multiple constraints, or optimization</complex>
    </reasoning_depth>
    <project_context>
      <when_needed>Examine codebase structure, dependencies, or existing patterns</when_needed>
      <when_skip>Greenfield features with no existing code dependencies</when_skip>
    </project_context>
  </step>

  <step name="clarify">
    <when>Request is ambiguous or could benefit from more detail</when>
    <how>
      <message>I'll create an optimized specification. First, let me clarify a few things:</message>
      <questions>
        <question>Specific ambiguous aspects</question>
        <question>Architectural decisions - frameworks, patterns, libraries</question>
        <question>Data sources and integrations</question>
        <question>What is this for? How will users interact with it?</question>
        <question>Who is the intended audience/user?</question>
        <question>Can you provide an example of specific aspect?</question>
      </questions>
      <closing>Please answer any that apply, or just say 'continue' if I have enough information.</closing>
    </how>
    <key_areas>
      <area>Architecture and design patterns to use</area>
      <area>Data sources and integrations needed</area>
      <area>Framework preferences and constraints</area>
      <area>Security and performance requirements</area>
      <area>Success criteria and verification methods</area>
    </key_areas>
  </step>

  <step name="confirm">
    <summary>Brief summary of what will be specified</summary>
    <complexity>Simple/moderate/complex</complexity>
    <approach>Key approach description</approach>
    <multiple_specs>If generating multiple specs, state number and execution strategy (parallel/sequential)</multiple_specs>
    <ask>Should I proceed, or would you like to adjust anything?</ask>
  </step>

  <step name="generate">
    <single_spec>
      <action>Generate one specification file following XML patterns</action>
      <save_as>[configured_path]/features/[number]-[name].md</save_as>
    </single_spec>
    <multiple_specs>
      <action>Generate 2-4 specifications with clear, focused objectives</action>
      <save_as>[configured_path]/features/[N]-[name].md, [N+1]-[name].md, etc.</save_as>
      <requirement>Each specification self-contained and executable independently</requirement>
    </multiple_specs>
    <naming>
      <number_format>001, 002, 003 (check existing files for next number)</number_format>
      <name_format>lowercase, hyphen-separated, max 5 words</name_format>
      <example>[configured_path]/features/001-implement-user-authentication.md</example>
    </naming>
    <file_contents>
      <content>ONLY the specification content, no explanations or metadata</content>
      <format>Full XML structure with semantic tags</format>
      <ready>Ready to be executed by dev-execute skill</ready>
    </file_contents>
    <note>configured_path comes from dev_docs_directory in root CLAUDE.md, defaults to ./.dev-docs</note>
  </step>
</specification_process>

<xml_patterns>
  <pattern name="simple_feature">
    <when>Single file, clear goal, straightforward implementation</when>
    <structure><![CDATA[
<objective>
[Clear statement of what needs to be done]
Brief explanation of the goal.
</objective>

<context>
[Project context, tech stack, relevant constraints]
@[relevant files to examine if needed]
Read CLAUDE.md for project conventions if it exists.
</context>

<requirements>
[Specific requirements]
Be explicit about what should be implemented.
</requirements>

<implementation>
[Approach to follow]
[What to avoid and WHY]
</implementation>

<output>
Create/modify files with relative paths:
- `./path/to/file.ext` - [what this file should contain]
</output>

<verification>
Before declaring complete, verify your work:
- [Specific test or check to perform]
- [How to confirm the solution works]

After implementing this feature, provide a "Suggested Manual Testing Steps" section with specific, actionable steps for the user to verify the feature works correctly.
</verification>

<success_criteria>
[Clear, measurable criteria for completion]
</success_criteria>
    ]]></structure>
  </pattern>

  <pattern name="standard_feature">
    <when>Multiple files, moderate complexity, clear requirements</when>
    <structure><![CDATA[
<objective>
[Clear statement of what feature needs to be built]
Explain the end goal and why this feature matters.
</objective>

<context>
[Project type, tech stack, relevant constraints]
[Who will use this feature, what it's for]
@[relevant files to examine]
Read CLAUDE.md for project conventions if it exists.
</context>

<requirements>
[Specific functional requirements]
[Performance or quality requirements]
[User experience requirements]
Be explicit about what should be implemented.
</requirements>

<implementation>
[Specific approaches or patterns to follow]
[Architecture decisions and rationale]
[What to avoid and WHY - explain the reasoning behind constraints]
</implementation>

<output>
Create/modify files with relative paths:
- `./path/to/file.ext` - [what this file should contain]
- `./path/to/another.ext` - [purpose of this file]
</output>

<verification>
Before declaring complete, verify your work:
- [Specific test or check to perform]
- [How to confirm the solution works]
- [Integration testing requirements]

After implementing this feature, provide a "Suggested Manual Testing Steps" section with specific, actionable steps for the user to verify the feature works correctly.
</verification>

<success_criteria>
[Clear, measurable criteria for completion]
[User acceptance criteria]
</success_criteria>
    ]]></structure>
  </pattern>

  <pattern name="complex_feature">
    <when>Multi-file, architectural decisions, research needed, multiple approaches</when>
    <structure><![CDATA[
<objective>
[Clear statement of what feature needs to be built]
Explain the end goal and why this feature matters.
</objective>

<research>
[Codebase areas to explore]
[Patterns or conventions to discover]
@[files or directories to examine]
![commands to gather information]
Thoroughly analyze existing patterns before implementing.
</research>

<context>
[Project type, tech stack, relevant constraints]
[Who will use this feature, what it's for]
Read CLAUDE.md for project conventions if it exists.
</context>

<requirements>
[Specific functional requirements]
[Performance or quality requirements]
[User experience requirements]
[How new feature should integrate with existing code]
Be explicit about what should be implemented.
</requirements>

<implementation>
[Specific approaches or patterns to follow]
[Architecture decisions and rationale]
[What to avoid and WHY - explain the reasoning behind constraints]
Deeply consider multiple approaches before selecting optimal one.
For ambitious features: Include as many relevant features as possible. Go beyond the basics to create a fully-featured implementation.
For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.
</implementation>

<output>
Create/modify files with relative paths:
- `./path/to/file.ext` - [what this file should contain]
- `./path/to/another.ext` - [purpose of this file]
</output>

<verification>
Before declaring complete, verify your work:
- [Specific test or check to perform]
- [How to confirm the solution works]
- [Integration testing requirements]
- [How to verify the implementation matches existing patterns]

After implementing this feature, provide a "Suggested Manual Testing Steps" section with specific, actionable steps for the user to verify the feature works correctly.
</verification>

<success_criteria>
[Clear, measurable criteria for completion]
[User acceptance criteria]
[Performance benchmarks if applicable]
</success_criteria>
    ]]></structure>
  </pattern>
</xml_patterns>

<construction_guidelines>
  <always_include>
    <item>XML tag structure with clear, semantic tags</item>
    <item>Contextual information: Why this feature matters, what it's for, who will use it</item>
    <item>Explicit, specific instructions: Exactly what to implement</item>
    <item>Sequential steps: Use numbered lists for clarity</item>
    <item>File output instructions using relative paths: ./filename or ./subfolder/filename</item>
    <item>Reference to reading CLAUDE.md for project conventions</item>
    <item>Explicit success criteria within success_criteria tags</item>
    <item>Verification steps within verification tags</item>
    <item>Testing step generation instruction: "After implementing this feature, provide a 'Suggested Manual Testing Steps' section..."</item>
  </always_include>

  <conditionally_include>
    <extended_thinking>
      <when>Complex reasoning, multiple constraints, optimization needed</when>
      <phrases>thoroughly analyze, consider multiple approaches, deeply consider, explore multiple solutions</phrases>
      <skip>Simple, straightforward features</skip>
    </extended_thinking>
    <go_beyond_basics>
      <when>Creative or ambitious features</when>
      <example>Include as many relevant features as possible. Go beyond the basics to create a fully-featured implementation.</example>
      <skip>Simple bug fixes or minimal changes</skip>
    </go_beyond_basics>
    <why_explanations>
      <when>Constraints or requirements need justification</when>
      <example>Instead of "Never use ellipses", write "Your response will be read aloud, so never use ellipses since text-to-speech can't pronounce them"</example>
      <include_for>All moderate and complex tasks</include_for>
    </why_explanations>
    <parallel_tool_calling>
      <when>Agentic or multi-step workflows</when>
      <guidance>For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.</guidance>
      <skip>Simple single-step tasks</skip>
    </parallel_tool_calling>
    <reflection_after_tools>
      <when>Complex agentic tasks</when>
      <guidance>After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding.</guidance>
    </reflection_after_tools>
    <additional_tags>
      <research>When codebase exploration is needed</research>
      <validation>For tasks requiring verification</validation>
      <examples>For complex or ambiguous requirements</examples>
      <constraints>For specific limitations</constraints>
    </additional_tags>
  </conditionally_include>

  <intelligence_principles>
    <principle name="clarity_first">If anything is unclear, ask before proceeding. Test: Would a colleague with minimal context understand this specification?</principle>
    <principle name="context_critical">Always include WHY the feature matters, WHO it's for, and WHAT it will be used for</principle>
    <principle name="be_explicit">Generate specifications with explicit, specific instructions. For ambitious features, include "go beyond the basics."</principle>
    <principle name="scope_assessment">Simple features get concise specs. Complex features get comprehensive structure with extended thinking triggers.</principle>
    <principle name="context_loading">Only request file reading when feature explicitly requires understanding existing code. Skip for greenfield features.</principle>
    <principle name="precision_over_brevity">Default to precision. A longer, clear specification beats a short, ambiguous one.</principle>
    <principle name="tool_integration">Include MCP servers only when explicitly mentioned or obviously needed. Use bash for environment checking. File references should be specific.</principle>
    <principle name="output_clarity">Every specification must specify exactly where to save outputs using relative paths</principle>
    <principle name="verification_always">Every specification should include clear success criteria and verification steps</principle>
    <principle name="testing_always">Every specification must instruct implementer to provide suggested manual testing steps</principle>
  </intelligence_principles>
</construction_guidelines>

<after_generation>
  <single_spec>
    <message>Saved specification to [configured_path]/features/[number]-[name].md</message>
    <options>
      <option number="1">Execute feature now (using dev-execute) - implements code and provides testing steps</option>
      <option number="2">Review/edit specification first</option>
      <option number="3">Save for later</option>
    </options>
    <note>After execution, feature will remain in [configured_path]/features/ for testing. Confirm completion after testing to archive.</note>
    <ask>Choose (1-3):</ask>
  </single_spec>

  <multiple_parallel>
    <message>Saved specifications: [list files]</message>
    <strategy>Execution strategy: These can run in PARALLEL (independent components, no shared files)</strategy>
    <options>
      <option number="1">Execute all in parallel now (launches N sub-agents simultaneously)</option>
      <option number="2">Execute sequentially instead</option>
      <option number="3">Review/edit specifications first</option>
    </options>
    <note>After execution, features will remain in [configured_path]/features/ for testing. Confirm completion after testing to archive.</note>
    <ask>Choose (1-3):</ask>
  </multiple_parallel>

  <multiple_sequential>
    <message>Saved specifications: [list files]</message>
    <strategy>Execution strategy: These must run SEQUENTIALLY (dependencies: [N] → [N+1] → [N+2])</strategy>
    <options>
      <option number="1">Execute sequentially now (one completes before next starts)</option>
      <option number="2">Execute first specification only ([number]-[name].md)</option>
      <option number="3">Review/edit specifications first</option>
    </options>
    <note>After each execution, feature will remain in [configured_path]/features/ for testing. Confirm completion after testing before next executes.</note>
    <ask>Choose (1-3):</ask>
  </multiple_sequential>

  <execution_invocation>
    <when>User chooses to execute</when>
    <action>Invoke dev-execute skill with appropriate parameters</action>
  </execution_invocation>
</after_generation>

<setup_requirements>
  <before_saving>
    <step>Run directory configuration workflow to determine spec directory path</step>
    <step>Check if configured directory exists</step>
    <step>If not, create it: mkdir -p [configured_path]/features</step>
    <step>Determine next number: ls [configured_path]/features/ 2>/dev/null | sort -V | tail -1</step>
    <step>If no files exist, start with 001</step>
  </before_saving>
  <note>Configured path comes from dev_docs_directory in root CLAUDE.md, defaults to ./.dev-docs</note>
</setup_requirements>

<examples>
  <example name="dashboard_clarification">
    <user_request>Build a dashboard</user_request>
    <clarification_needed>What kind of dashboard? Admin, analytics, user-facing? What data should it display? Who will use it?</clarification_needed>
    <complexity>Requires clarification before proceeding</complexity>
  </example>

  <example name="auth_clarification">
    <user_request>Add authentication</user_request>
    <clarification_needed>What type? JWT, OAuth, session-based? Which providers? What's the security context?</clarification_needed>
    <complexity>Multiple approaches possible, need to clarify</complexity>
  </example>

  <example name="realtime_clarification">
    <user_request>Implement real-time updates</user_request>
    <clarification_needed>What technology? WebSockets, SSE, polling? What data needs real-time updates?</clarification_needed>
    <complexity>Technical approach needs to be determined</complexity>
  </example>

  <example name="performance_clarification">
    <user_request>Optimize performance</user_request>
    <clarification_needed>What specific performance issues? Load time, memory, database queries? What are current metrics?</clarification_needed>
    <complexity>Need to understand problem before specifying solution</complexity>
  </example>

  <example name="api_clarification">
    <user_request>Create API endpoints</user_request>
    <clarification_needed>What resources? What operations (CRUD)? REST or GraphQL? Authentication required?</clarification_needed>
    <complexity>Scope and approach need clarification</complexity>
  </example>

  <example name="simple_bug_fix">
    <user_request>Fix the login button that's not responding on mobile</user_request>
    <analysis>Simple, single file, clear goal</analysis>
    <specification_type>Lightweight specification with objective, context, requirements, implementation, verification</specification_type>
    <testing_included>Yes - instruction to provide testing steps for mobile devices</testing_included>
  </example>

  <example name="complex_auth_system">
    <user_request>Build a user authentication system with OAuth support for Google and GitHub</user_request>
    <analysis>Complex, multi-file, architectural decisions, research needed</analysis>
    <specification_type>Comprehensive specification with research, extended thinking, parallel tool calling</specification_type>
    <testing_included>Yes - instruction to provide detailed testing steps for OAuth flows</testing_included>
  </example>

  <example name="moderate_form_validation">
    <user_request>Implement form validation for the signup form</user_request>
    <analysis>Moderate complexity, multiple validation rules, some design decisions</analysis>
    <specification_type>Standard specification with requirements, implementation guidance, verification</specification_type>
    <testing_included>Yes - instruction to provide testing steps for various validation scenarios</testing_included>
  </example>
</examples>

<related_skills>
  <skill name="dev-orchestrator">Orchestrator that guides the overall feature development workflow</skill>
  <skill name="dev-execute">Executes the generated specifications with two-phase testing workflow</skill>
</related_skills>

</skill>
