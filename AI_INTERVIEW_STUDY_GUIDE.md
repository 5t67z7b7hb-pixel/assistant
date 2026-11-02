# AI and Generative AI Interview Notes

Use these as concise study references. Explain the concept asked about; do not dump the whole guide into an answer.

## Core GenAI concepts
An LLM is a neural network, commonly transformer-based, that predicts a distribution over the next token from the prompt and prior tokens. Tokens are text units and are not always whole words. The context window bounds the tokens available for instructions, history, retrieved context, and output. Prompting should state the task, relevant context, constraints, and desired output. Sampling selects from token probabilities: temperature affects randomness and top-p limits choices to a cumulative probability mass; neither adds factual knowledge. Model limits include hallucinations, stale or missing knowledge, ambiguity, long-context failures, bias, and inconsistent reasoning. Ground claims in evidence and validate important outputs.

## RAG
Retrieval-Augmented Generation supplies external evidence at inference time; it is not fine-tuning. Ingest authoritative documents, parse/OCR and clean them, preserve source IDs and metadata, chunk on useful structural or semantic boundaries, embed and index the chunks, then retrieve with vector or hybrid search. Apply access filters before returning content, rerank candidates when useful, and pass selected evidence to the model. Citations should identify the exact source, version, page, or section and support the attached claim. Keep content fresh with incremental updates, re-indexing, deletion of obsolete sources, and monitoring. Chunk size and overlap trade retrieval precision against context completeness; reranking can improve relevance at added latency and cost.

## MCP and MCP servers
MCP means Model Context Protocol. The host manages the user-facing session and policy; an MCP client communicates with a server. Servers can expose tools (actions or queries), resources (context/data), and prompts (reusable templates). A typical flow is capability discovery, a named tool request with structured arguments, server-side execution, and a result returned through the host. MCP standardizes the connection; it does not itself grant permissions, and an MCP server is not an LLM. Enforce identity and authorization in the application, validate tool schemas and arguments, use allowlists and least privilege, show tool actions, and require human approval for sensitive side effects. Treat tool descriptions and results as untrusted input. RAG is a retrieval-and-generation pattern; an MCP server can expose RAG search as a tool.

## Agentic AI
An AI agent combines a model with instructions, tools, and state to pursue a goal through an observe-decide-act loop. It may plan, call a tool, inspect the result, and continue or stop. Use agents when a task needs adaptive multi-step work; use a deterministic workflow for fixed, predictable steps. Reliable agent design uses narrow tools, explicit stop conditions, bounded retries, state tracking, and human approval for consequential actions.

## Guardrails and safety
Use layered controls: defend against direct and indirect prompt injection by treating user input, retrieved documents, and tool results as untrusted data; minimize or redact sensitive data; enforce tool authorization in application code; allowlist tools and apply least privilege; validate arguments and outputs against schemas and evidence; require human review for high-impact or low-confidence cases; and monitor with logs and adversarial tests. A prompt alone is not a security boundary. Measure helpfulness and safety.

## AI system architecture
A production knowledge architecture needs a named owner and canonical source for each domain, consistent metadata and taxonomies, tenant/user access control, provenance, and versioning. Its update workflow detects source changes, parses and validates content, re-indexes new versions, removes obsolete content, checks freshness, and keeps an audit trail. A production GenAI system commonly has a client, API/orchestration layer, model endpoint, optional RAG pipeline, optional MCP tools, and shared policy, observability, evaluation, and access-control layers. Keep secrets and authorization in the application, not the model prompt.

## Evaluation
Evaluate retrieval separately from answer generation. Measure retrieval precision, recall, and relevance; answer correctness and faithfulness; and citation accuracy (whether each cited source supports its claim). Track latency, including p50/p95, token and infrastructure cost, safety, privacy leakage, and robustness to prompt injection. Use representative labeled questions, expert review for high-impact cases, regression checks across model/index/prompt versions, and sampled production feedback.

## Claude and tool-use concepts
Claude is Anthropic's model family; this application currently calls a local Ollama model, not Claude. Anthropic's Claude documentation is useful for general prompt and tool-use design: give clear instructions and relevant context, use examples and structured sections, and specify the desired output. In a tool-use cycle, the model requests a named tool with structured inputs; the application validates and executes it, returns the tool result, and lets the model produce a final response. The model does not execute the tool by itself.

## Source references
- Anthropic Claude prompting guide: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables
- MCP protocol and SDK concepts: https://modelcontextprotocol.io/
- MCP TypeScript SDK overview: https://ts.sdk.modelcontextprotocol.io/v2/
- Foundational RAG paper (Lewis et al., NeurIPS 2020): https://arxiv.org/abs/2005.11401
