# Building an Agentic AI Bot

**Domain:** Agentic AI application design  
**Purpose:** A practical blueprint for building an AI system that can use
tools to complete bounded multi-step tasks.

## What makes a system agentic

An agentic AI application combines a model with instructions, available
actions (tools), and state. It can observe a request or result, decide on a
next step, request a tool call, inspect the tool result, and continue until it
finishes or reaches a stopping condition. The model proposes actions; the
application remains responsible for authorization, validation, execution, and
side effects.

Use an agent when the right next step depends on intermediate results. Prefer
a deterministic workflow when the steps are known in advance: fixed workflows
are often easier to test, explain, and operate.

## Basic architecture

1. **User interface:** Captures requests and presents progress, approval
   prompts, and results.
2. **Orchestrator:** Maintains state, applies policy, calls the model, and
   enforces iteration and time limits.
3. **Model:** Interprets context and may propose a structured tool call or a
   final response.
4. **Tool adapters:** Validate arguments and call approved APIs or services.
5. **Data and memory:** Supply scoped context. Distinguish temporary
   conversation state from durable user-approved memory.
6. **Observability and evaluation:** Record safe operational events and
   measure quality, safety, latency, and cost.

Keep application policy outside the model's free-form text. A prompt is not
an authorization boundary.

## Build process

### 1. Define one bounded job

Describe the user, goal, acceptable inputs, expected output, and explicit
non-goals. Identify the cost of a wrong answer or action. Start with one
workflow rather than a general-purpose autonomous assistant.

### 2. Choose the simplest execution pattern

Map the process. Use ordinary code for known branches, retries, and validation.
Use model decisions only where interpretation or adaptive planning adds value.
If tools and state are unnecessary, a regular model call may be sufficient.

### 3. Design narrow tools

Each tool should have one purpose, a clear name, a typed input schema, and a
well-defined result. Prefer read-only tools initially. Validate inputs in
application code, constrain identifiers and options, enforce user permissions
at the service boundary, and return only the data the model needs.

Do not expose a generic shell, arbitrary URL fetch, unrestricted database
query, or broad administrative API as a convenience tool. Use explicit
allowlists and least privilege.

### 4. Implement a bounded tool loop

The following pseudocode illustrates the control flow; it is not tied to a
specific model SDK:

```text
state = validated_request_and_context()

for step in 1..MAX_STEPS:
    response = model.generate(state, allowed_tool_schemas)

    if response is a final answer:
        validate_and_return(response)

    call = parse_structured_tool_call(response)
    tool = lookup_allowlisted_tool(call.name)
    arguments = validate_schema_and_authorization(tool, call.arguments)

    if tool.has_consequential_side_effect:
        require_explicit_user_approval(arguments)

    result = execute_with_timeout_and_audit(tool, arguments)
    state = append_bounded_result(state, result)

return safe_stop_message()
```

Handle malformed calls and tool errors explicitly. Apply per-tool timeouts,
bounded retries only for appropriate transient failures, a maximum number of
model/tool steps, and limits on input, output, and total cost. Never treat a
tool failure as a successful result.

### 5. Treat all external content as untrusted

User messages, retrieved documents, web pages, and tool results may contain
instructions that conflict with application policy. Treat them as data, not
authority. Do not let retrieved text authorize an action or override
permissions. Keep secrets out of prompts and model-visible tool results.

### 6. Require human approval for consequential actions

Preview what will happen, show the target and relevant values, and ask for
approval immediately before irreversible or high-impact actions such as
sending messages, changing records, making purchases, or deleting data.
Approval should be scoped to the specific action and inputs; it should not
grant ongoing broad permissions.

### 7. Test and deploy incrementally

Build a representative evaluation set including ordinary requests,
ambiguous requests, invalid tool arguments, tool failures, permission
boundaries, malicious instructions in retrieved content, and requests that
should be refused or escalated. Test the orchestration loop and each tool
adapter separately. Start with read-only or simulated actions, then expand
capability only after review.

## Reliability and safety checklist

- [ ] Goal, scope, and stop conditions are explicit.
- [ ] Tools have narrow schemas and enforce authorization server-side.
- [ ] Iterations, retries, latency, context, and cost are bounded.
- [ ] Side effects require suitable confirmation and are auditable.
- [ ] Tool outputs and retrieved content are treated as untrusted.
- [ ] Errors are visible and do not become success-shaped results.
- [ ] Sensitive data is minimized, protected, and retained only as needed.
- [ ] Monitoring avoids logging secrets and unnecessary personal data.
- [ ] Evaluation covers correctness, tool choice, safety, and regressions.
- [ ] Users can understand when the bot is uncertain or cannot proceed.

## Evaluation measures

Measure task completion and factual correctness, but also tool selection,
argument validity, authorization behavior, refusal and escalation quality,
citation or evidence quality when retrieval is used, and resilience to
injection. Track latency and cost per completed task. Review failures and
update the evaluation set as real use cases change.

## Common mistakes

- Giving the model tools that are broader than the actual task requires.
- Letting the model decide its own permissions.
- Repeating failed calls without an explicit retry policy.
- Treating a plausible model response as proof that an external action
  succeeded.
- Storing every conversation indefinitely as memory.
- Using an agent for a deterministic workflow with no need for adaptive
  decisions.
- Testing only successful examples or relying on a prompt as the only guard.

## Further reading

- Model Context Protocol: https://modelcontextprotocol.io/
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework

Framework APIs and model capabilities change. Consult the current
documentation for the chosen SDK, model, and deployment environment.
