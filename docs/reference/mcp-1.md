# Top MCP Servers (Cross-language friendly) — Sorted by “importance”
> Notes: 
> - “Install (Claude)” uses the Claude Desktop CLI pattern: `claude mcp add <Name> -s user -- <command and args>` (see examples in MCP docs and community scripts).  
> - Use `npx -y` for Node packages, `uvx`/`pipx run` for Python, or a binary/`go run` for Go.  
> - Sources you can check for details & updates:  
>   - Official examples: https://modelcontextprotocol.io/examples  
>   - How to connect in Claude: https://modelcontextprotocol.io/docs/develop/connect-local-servers  
>   - Awesome/registries: https://github.com/wong2/awesome-mcp-servers , https://github.com/punkpeye/awesome-mcp-servers , https://mcpservers.org/ , https://www.pulsemcp.com/servers  
>   - One-command Claude installs pattern: https://www.reddit.com/r/ClaudeAI/comments/1jf4hnt/ (community)

| # | Name | What it does (1-liner) | Role / Persona | Install (Claude) — example command |
|---:|---|---|---|---|
| 1 | GitHub (official) | Full GitHub API: repos, issues, PRs, code search, workflows. | SW Eng, SRE, Platform, SecEng | `claude mcp add github -- npx -y @modelcontextprotocol/server-github` |
| 2 | Git (repo local/remote) | Read/search/branch/diff/commit utilities over Git repos. | SW Eng, Release Eng | `claude mcp add git -- npx -y @mseep/git-mcp-server` |
| 3 | Fetch (web fetch→Markdown) | Safe HTTP(S) retrieval, chunking/convert to MD. | Research, Eng, Analyst | `claude mcp add fetch -- npx -y @smithery/mcp-fetch` |
| 4 | Filesystem (scoped) | Read/write files in allow-listed paths. | All devs | `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem` |
| 5 | Sequential Thinking | Structured multi-step planning/thought scaffolding. | All | `claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking` |
| 6 | OpenAPI | Load OpenAPI specs → typed tool calls to APIs. | Backend, API, Integrations | `claude mcp add openapi -- npx -y @modelcontextprotocol/server-openapi` |
| 7 | Kubernetes (community) | Introspect/apply/describe/logs/exec (guarded). | DevOps, SRE, Platform | `claude mcp add kubernetes -- npx -y mcp-server-kubernetes` |
| 8 | Kubernetes (Red Hat/containers) | K8s/OpenShift management server. | DevOps, SRE | `claude mcp add k8s -- npx -y containers/kubernetes-mcp-server` |
| 9 | Docker / Containerd | Manage containers/images locally (guarded). | Dev, DevOps | `claude mcp add containerd -- npx -y mcp-containerd` |
| 10 | PostgreSQL (Pro/community) | Query/admin Postgres with guardrails. | Data Eng, App Dev | `claude mcp add postgres -- npx -y postgres-mcp` |
| 11 | PostgreSQL (alt) | Kysely/ORM backed Postgres access. | Data Eng | `claude mcp add postgres-kysely -- npx -y abiswas97-postgres-mcp-server` |
| 12 | MySQL/MariaDB | Query/admin MySQL (scoped). | Data Eng | `claude mcp add mysql -- npx -y mcp-mysql-server` |
| 13 | SQLite | Local DB workbench for prototyping. | Data Eng, App Dev | `claude mcp add sqlite -- npx -y mcp-sqlite-server` |
| 14 | DuckDB | Local analytics and parquet/csv crunching. | Data Eng, Analytics | `claude mcp add duckdb -- npx -y mcp-duckdb-server` |
| 15 | BigQuery | Read/write datasets with policy guards. | Data Platform | `claude mcp add bigquery -- npx -y mcp-bigquery-server` |
| 16 | Snowflake | Warehousing ops: query/stage/files. | Data Platform | `claude mcp add snowflake -- npx -y mcp-snowflake-server` |
| 17 | Redis | KV ops, pub/sub helpers. | Backend, Caching | `claude mcp add redis -- npx -y mcp-redis-server` |
| 18 | Elasticsearch / OpenSearch | Search/index ops. | Search, SRE | `claude mcp add elastic -- npx -y mcp-elasticsearch-server` |
| 19 | Neo4j | Graph queries (Cypher). | Graph Eng, Data Sci | `claude mcp add neo4j -- npx -y mcp-neo4j-server` |
| 20 | Weaviate | Vectors/collections and semantic search. | RAG Eng | `claude mcp add weaviate -- npx -y mcp-weaviate-server` |
| 21 | Qdrant | Vector DB ops. | RAG Eng | `claude mcp add qdrant -- npx -y mcp-qdrant-server` |
| 22 | Pinecone | Vector DB ops. | RAG Eng | `claude mcp add pinecone -- npx -y mcp-pinecone-server` |
| 23 | Milvus | Vector DB ops. | RAG Eng | `claude mcp add milvus -- npx -y mcp-milvus-server` |
| 24 | S3 | Buckets/objects (scoped). | Platform, Data Eng | `claude mcp add s3 -- npx -y mcp-s3-server` |
| 25 | GCS | Google Cloud Storage ops. | Platform | `claude mcp add gcs -- npx -y mcp-gcs-server` |
| 26 | Azure Blob | Blob containers ops. | Platform | `claude mcp add azure-blob -- npx -y mcp-azure-blob-server` |
| 27 | Cloudflare R2 | Object storage ops. | Platform | `claude mcp add r2 -- npx -y mcp-r2-server` |
| 28 | Terraform | Plan/apply/read state with guardrails. | Platform, IaC | `claude mcp add terraform -- npx -y hashicorp/terraform-mcp-server` |
| 29 | Helm | Template/install/upgrade with dry-runs. | Platform, K8s | `claude mcp add helm -- npx -y mcp-helm-server` |
| 30 | ArgoCD | App sync/status/diff operations. | Platform, DevOps | `claude mcp add argocd -- npx -y mcp-argocd-server` |
| 31 | GitLab | Issues/MRs/pipelines APIs. | SW Eng, Platform | `claude mcp add gitlab -- npx -y mcp-gitlab-server` |
| 32 | Bitbucket | Repos/PRs/pipelines APIs. | SW Eng | `claude mcp add bitbucket -- npx -y mcp-bitbucket-server` |
| 33 | Jira | Issues/queries/transitions. | PM, Eng Mgr | `claude mcp add jira -- npx -y mcp-jira-server` |
| 34 | Confluence | Pages/search/edit. | PM, Docs | `claude mcp add confluence -- npx -y mcp-confluence-server` |
| 35 | Linear | Issues/projects. | Eng/PM | `claude mcp add linear -- npx -y mcp-linear-server` |
| 36 | Notion | DB/pages read/write. | PM, Docs, Eng | `claude mcp add notion -- npx -y mcp-notion-server` |
| 37 | Slack | Channels/threads/file ops (guarded). | Eng, Support | `claude mcp add slack -- npx -y mcp-slack-server` |
| 38 | Teams | Chat/channels (enterprise). | Eng, Ops | `claude mcp add teams -- npx -y mcp-teams-server` |
| 39 | Gmail | Mail read/draft/send (scoped). | Support, Ops | `claude mcp add gmail -- npx -y mcp-gmail-server` |
| 40 | Google Drive | Files/search/permissions. | All | `claude mcp add gdrive -- npx -y mcp-google-drive-server` |
| 41 | Google Calendar | Events/availability. | PM, Eng Mgr | `claude mcp add gcal -- npx -y mcp-google-calendar-server` |
| 42 | Outlook/Office 365 | Mail/Calendar/Drive. | Enterprise IT | `claude mcp add msgraph -- npx -y mcp-msgraph-server` |
| 43 | GitHub Actions | Workflows/runs/artifacts. | DevOps | `claude mcp add gha -- npx -y @modelcontextprotocol/server-github-actions` |
| 44 | Vercel | Deployments/env vars/logs. | Frontend/Platform | `claude mcp add vercel -- npx -y mcp-vercel-server` |
| 45 | Netlify | Sites/deploys. | Frontend | `claude mcp add netlify -- npx -y mcp-netlify-server` |
| 46 | Cloudflare | DNS/Workers/KV. | Platform, Edge | `claude mcp add cloudflare -- npx -y mcp-cloudflare-server` |
| 47 | AWS (boto3 wrapper) | Multi-service AWS ops (scoped). | Cloud Eng | `claude mcp add aws -- uvx mcp-aws-server` |
| 48 | GCP (google-cloud) | GCP APIs via service account. | Cloud Eng | `claude mcp add gcp -- uvx mcp-gcp-server` |
| 49 | Azure (azure-sdk) | Azure resources ops. | Cloud Eng | `claude mcp add azure -- uvx mcp-azure-server` |
| 50 | OpenAI | Call models/tools/log usage. | AI Eng | `claude mcp add openai -- npx -y mcp-openai-server` |
| 51 | Anthropic | Anthropic API orchestration. | AI Eng | `claude mcp add anthropic -- npx -y mcp-anthropic-server` |
| 52 | Ollama | Local models, embeddings. | AI Eng, RAG | `claude mcp add ollama -- npx -y mcp-ollama-server` |
| 53 | Llama.cpp | Local CPU/GPU models. | AI Eng | `claude mcp add llamacpp -- npx -y mcp-llamacpp-server` |
| 54 | Hugging Face | Datasets/models inference. | AI Eng | `claude mcp add huggingface -- npx -y mcp-hf-server` |
| 55 | Langfuse | Tracing/observability for LLM runs. | AI Eng, MLOps | `claude mcp add langfuse -- npx -y mcp-langfuse-server` |
| 56 | Sentry | Error ingest/search/issue links. | Eng, SRE | `claude mcp add sentry -- npx -y mcp-sentry-server` |
| 57 | Datadog | Metrics/logs/APM/incidents. | SRE, SecOps | `claude mcp add datadog -- npx -y mcp-datadog-server` |
| 58 | New Relic | APM/infra/query NRQL. | SRE | `claude mcp add newrelic -- npx -y mcp-newrelic-server` |
| 59 | Grafana | Dashboards/Loki/Tempo queries. | SRE | `claude mcp add grafana -- npx -y mcp-grafana-server` |
| 60 | Prometheus | Metrics queries/alerts. | SRE | `claude mcp add prometheus -- npx -y mcp-prometheus-server` |
| 61 | PagerDuty | Incidents/on-call schedule. | SRE, Support | `claude mcp add pagerduty -- npx -y mcp-pagerduty-server` |
| 62 | Opsgenie | Alerts/on-call. | SRE | `claude mcp add opsgenie -- npx -y mcp-opsgenie-server` |
| 63 | ServiceNow | Tickets/CMDB. | ITSM, SecOps | `claude mcp add servicenow -- npx -y mcp-servicenow-server` |
| 64 | Splunk | Search/SPL dashboards. | SecOps, SRE | `claude mcp add splunk -- npx -y mcp-splunk-server` |
| 65 | ELK Utilities | Pipelines/index mgmt helpers. | SecOps | `claude mcp add elk -- npx -y mcp-elk-server` |
| 66 | Vault | KV/Transit (strict scope) | SecEng, Platform | `claude mcp add vault -- npx -y mcp-vault-server` |
| 67 | 1Password | Secrets retrieval (scoped). | Eng, Sec | `claude mcp add 1password -- npx -y mcp-1password-server` |
| 68 | Stripe | Customers/payments/payouts. | Fintech, Eng | `claude mcp add stripe -- npx -y mcp-stripe-server` |
| 69 | Twilio | SMS/voice/email flows. | Eng, Ops | `claude mcp add twilio -- npx -y mcp-twilio-server` |
| 70 | SendGrid/Postmark | Transactional email. | Eng, Growth | `claude mcp add postmark -- npx -y ActiveCampaign/postmark-mcp` |
| 71 | Browserless/Playwright | Headless browse/scrape/test. | QA, E2E, Research | `claude mcp add playwright -- npx -y mcp-playwright-server` |
| 72 | Puppeteer | Headless Chrome control. | QA, Growth | `claude mcp add puppeteer -- npx -y mcp-puppeteer-server` |
| 73 | Serper/Google CSE | Web search API wrapper. | Research | `claude mcp add serper -- npx -y mcp-serper-server` |
| 74 | DuckDuckGo | DDG search (no key). | Research | `claude mcp add ddg -- npx -y mcp-ddg-server` |
| 75 | NPM Registry | Search/readme/meta lookup. | JS/TS Dev | `claude mcp add npm -- npx -y npm-search-mcp-server` |
| 76 | PyPI | Package info/security flags. | Python Dev | `claude mcp add pypi -- uvx mcp-pypi-server` |
| 77 | Go Proxy | Module info/versions. | Go Dev | `claude mcp add goproxy -- npx -y mcp-go-proxy-server` |
| 78 | Make/CLI Runner | Run whitelisted shell tasks. | All devs | `claude mcp add shell -- npx -y mcp-shell-server --allow make,test,go,uv` |
| 79 | Diff/Patch | Generate/apply patches. | SW Eng | `claude mcp add patch -- npx -y mcp-patch-server` |
| 80 | Semgrep | Static analysis scans. | AppSec, Eng | `claude mcp add semgrep -- npx -y mcp-semgrep-server` |
| 81 | Trivy | Container/IaC scans. | SecEng, DevOps | `claude mcp add trivy -- npx -y mcp-trivy-server` |
| 82 | OPA/Rego | Policy test/eval. | SecEng, Platform | `claude mcp add opa -- npx -y mcp-opa-server` |
| 83 | Cedar (AWS) | Cedar policy evaluate. | SecEng | `claude mcp add cedar -- npx -y mcp-cedar-server` |
| 84 | OpenAPI Linter | Spectral/lint/fix. | API Eng | `claude mcp add spectral -- npx -y mcp-spectral-server` |
| 85 | SwaggerHub | Spec sync/publish. | API Eng | `claude mcp add swaggerhub -- npx -y mcp-swaggerhub-server` |
| 86 | Postman | Collections/run tests. | API/QA | `claude mcp add postman -- npx -y mcp-postman-server` |
| 87 | Terraform Cloud | Runs/vars/state. | Platform | `claude mcp add tfc -- npx -y mcp-terraform-cloud-server` |
| 88 | Pulumi | Stacks/resources (guarded). | Platform | `claude mcp add pulumi -- npx -y mcp-pulumi-server` |
| 89 | FastMail/IMAP | Generic IMAP operations. | Ops, Support | `claude mcp add imap -- npx -y mcp-imap-server` |
| 90 | Calendar ICS | Parse/merge/emit ICS. | PM, Eng Mgr | `claude mcp add ics -- npx -y mcp-ics-server` |
| 91 | CSV/Parquet | Inspect/filter/transform. | Data Eng | `claude mcp add parquet -- npx -y mcp-parquet-server` |
| 92 | PDF Tools | Extract/summarize/annotate. | Research, Legal | `claude mcp add pdf -- uvx mcp-pdf-server` |
| 93 | Obsidian | Vault read/write/search. | Docs, PKM | `claude mcp add obsidian -- npx -y mcp-obsidian-server` |
| 94 | MediaWiki | Query/edit pages. | Docs, Research | `claude mcp add mediawiki -- npx -y mcp-mediawiki-server` |
| 95 | Wikipedia/OpenLibrary | Encyclopedia/books search. | Research | `claude mcp add openlibrary -- npx -y mcp-open-library` |
| 96 | YouTube | Search/captions/chapters. | Growth, Research | `claude mcp add youtube -- npx -y mcp-youtube-server` |
| 97 | Jira Service Mgmt | Helpdesk/requests. | ITSM | `claude mcp add jsm -- npx -y mcp-jsm-server` |
| 98 | Terraform Docs | Resource schema lookup. | IaC Eng | `claude mcp add tfdocs -- npx -y mcp-terraform-docs-server` |
| 99 | Secrets Scanner | Git leaks scanner. | SecEng | `claude mcp add secrets -- npx -y mcp-gitleaks-server` |
| 100 | Memory (unified) | Long-term semantic memory store. | All | `claude mcp add memory -- npx -y mcp-memory-service` |

---

## Usage tips
- Run servers locally once to confirm the binary/SDK is installed (e.g., `npx -y <pkg> --help`, `uvx <pkg> --help`).  
- If `npx` has PATH/nvm issues, prefer global install (`npm i -g <pkg>`) then:  
  `claude mcp add <Name> -s user -- node $(npm root -g)/<pkg>/bin/index.js`  
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector -- <your server cmd>`  
- For per-project config, run the same `claude mcp add ...` from that project folder (Claude Desktop will write project-level config).

