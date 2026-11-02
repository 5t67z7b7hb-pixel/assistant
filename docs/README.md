# Technical Knowledge Documents

This folder contains standalone, Markdown-formatted reference material for
Python, SQL, SAP, PlantUML, agentic AI, HTML, CSS, and process automation. The
documents are written with descriptive headings and examples so they can be
reviewed, searched, or prepared for a future knowledge-ingestion workflow.

## Documents

- [Python](python.md): language fundamentals, common patterns, testing, and
  maintainability.
- [SQL](sql.md): relational modeling, queries, transactions, safe application
  access, and performance.
- [SAP](sap.md): ERP concepts, major SAP products, application development,
  integration, security, and implementation practices.
- [PlantUML](plantuml.md): diagram syntax, common diagram types, examples, and
  rendering guidance.
- [Building an Agentic AI Bot](agentic-ai-bot.md): architecture, a staged
  implementation approach, tool-use controls, and evaluation.
- [HTML](html.md): semantic document structure, forms, accessibility, and
  browser behavior.
- [CSS](css.md): selectors, layout, responsive design, accessibility, and
  maintainable styling.
- [Process Automation](process-automation.md): process discovery, tool
  selection, implementation, controls, rollout, and measurement.

## Using this material with an AI model

Adding files to this folder does not train or modify the bundled model, and
the application does not automatically load these documents into a prompt.
To make the content available at answer time, a separate retrieval-augmented
generation (RAG) or other document-ingestion workflow must index the files and
provide relevant passages to the model. Fine-tuning is a separate process and
is not performed by adding documentation.

For reliable answers, keep source documents current, preserve each file name
and heading as metadata, retrieve only relevant sections, and have the model
distinguish general guidance from version-specific product behavior. Verify
SAP features, APIs, and licensing against the documentation for the exact
product and release in use.
