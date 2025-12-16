# Top 100 MCP servers — unified, sorted by practical usefulness (Go / TS-Node / Python)

> Columns: **Name | What it does | Role | Install (Claude)**.  
> • **Remote (URL)** = paste this into Claude → Settings → Connectors → “Add custom connector”.  
> • **Remote (Guide)** = service-specific doc for connecting the client.  
> • Locals use `npx` (Node) or `uvx` (Python). Replace paths/tokens to match your env.

| # | Name | What it does | Role | Install (Claude) |
|---:|---|---|---|---|
| 1 | Serena | LSP-grade code understanding & safe edits | Backend/Full-stack | `claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --project $(pwd)` |
| 2 | Context7 | Versioned docs/snippets grounding | All devs | **Remote (Guide):** https://github.com/upstash/context7 |
| 3 | GitHub (official) | Repos, issues, PRs, search | Eng/DevEx | `claude mcp add github -- npx -y @modelcontextprotocol/server-github` |
| 4 | Filesystem (official) | Scoped local FS | Any dev | `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /ABS/PATH` |
| 5 | Sequential Thinking | Multi-step planning scaffold | Any dev | `claude mcp add sequential -- npx -y @modelcontextprotocol/server-sequential-thinking` |
| 6 | SQLite | Local SQL workbench | App/Data | `claude mcp add sqlite -- uvx mcp-server-sqlite --db-path ./app.sqlite` |
| 7 | PostgreSQL (TS) | Postgres queries/schema | App/Data | `claude mcp add postgres -- npx -y @ahmetkca/mcp-server-postgres` |
| 8 | Playwright | Real browser automation | QA/Growth/Research | `claude mcp add playwright -- npx -y @playwright/mcp` |
| 9 | Kubernetes (local) | kubectl-like ops (scoped) | SRE/Platform | `claude mcp add k8s -- npx -y mcp-server-kubernetes` |
| 10 | Redis | KV/streams/vectors | Backend/RAG | `claude mcp add redis -- npx -y @mcpflow.io/mcp-redis` |
| 11 | OpenAPI Bridge | Any OpenAPI → tools | Backend/API | `claude mcp add openapi -- npx -y @iflow-mcp/openapi-mcp-server` |
| 12 | NPM Registry | Package/readme/meta search | JS/TS | `claude mcp add npm -- npx -y npm-search-mcp-server` |
| 13 | DuckDB | Local analytics over CSV/Parquet | Data/Analytics | `claude mcp add duckdb -- npx -y mcp-duckdb-server` |
| 14 | Elasticsearch | Search/index/query | Search/SRE | `claude mcp add elastic -- npx -y @mcp-labs/elasticsearch-mcp` |
| 15 | Meilisearch | Lightweight search | App dev | `claude mcp add meili -- npx -y @mcp-labs/meili-mcp` |
| 16 | Typesense | Fast search | App dev | `claude mcp add typesense -- npx -y @mcp-labs/typesense-mcp` |
| 17 | PostgREST | Postgres via REST bridge | App/Data | `claude mcp add postgrest -- npx -y @supabase/mcp-server-postgrest` |
| 18 | Firecrawl | Crawl → clean text (RAG) | Research | `claude mcp add firecrawl -- npx -y @mendableai/firecrawl-mcp` |
| 19 | Trivy | Container/IaC scans | Sec/DevOps | `claude mcp add trivy -- npx -y @aquasecurity/trivy-mcp` |
| 20 | Semgrep | SAST code scanning | AppSec | `claude mcp add semgrep -- npx -y @returntocorp/semgrep-mcp` |
| 21 | Gitleaks | Secret leakage scanner | SecEng | `claude mcp add gitleaks -- npx -y @zricethezav/gitleaks-mcp` |
| 22 | OPA/Rego | Policy eval/testing | Sec/Platform | `claude mcp add opa -- npx -y mcp-opa-server` |
| 23 | Cedar (AWS) | Cedar policy evaluate | SecEng | `claude mcp add cedar -- npx -y mcp-cedar-server` |
| 24 | Spectral | OpenAPI lint/fix | API Eng | `claude mcp add spectral -- npx -y mcp-spectral-server` |
| 25 | Terraform Docs | Resource schema lookup | IaC Eng | `claude mcp add tfdocs -- npx -y mcp-terraform-docs-server` |
| 26 | Helm | Chart template/install | K8s/Platform | `claude mcp add helm -- npx -y @mcp-labs/helm-mcp` |
| 27 | Argo CD | GitOps app mgmt | Platform | `claude mcp add argocd -- npx -y @mcp-labs/argocd-mcp` |
| 28 | Shell Tasks (guarded) | Allow-listed CLI (make/test) | Any dev | `claude mcp add shell -- npx -y mcp-shell-server --allow make,test,go,uv` |
| 29 | Patch/Diff | Create/apply patches | SW Eng | `claude mcp add patch -- npx -y mcp-patch-server` |
| 30 | PDF Tools | Extract/summarize/annotate | Research/Legal | `claude mcp add pdf -- uvx mcp-pdf-server` |
| 31 | **Notion (Remote)** | Workspace pages/DBs | PM/Docs/Eng | **Remote (Guide):** https://developers.notion.com/docs/mcp |
| 32 | **GitLab (Remote)** | Repos/MRs/pipelines | Eng/DevOps | **Remote (Guide):** https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/ |
| 33 | **Asana (Remote)** | Tasks/projects | PM/Eng | **Remote (URL):** https://mcp.asana.com/sse |
| 34 | **Atlassian (Remote)** | Jira/Confluence/Bitbucket | Eng/PM/Docs | **Remote (URL):** https://mcp.atlassian.com/v1/sse |
| 35 | **Cloudflare (Remote)** | DNS/Workers/KV/R2 | Platform/Edge | **Remote (Guide):** https://github.com/cloudflare/mcp-server-cloudflare |
| 36 | **Intercom (Remote)** | Support/triage | Support/PM | **Remote (URL):** https://mcp.intercom.com/sse |
| 37 | **Linear (Remote)** | Issues/projects | Eng/PM | **Remote (URL):** https://mcp.linear.app/sse |
| 38 | **PayPal (Remote)** | Invoices/sales | Commerce | **Remote (URL):** https://mcp.paypal.com/sse |
| 39 | **Plaid (Remote)** | Metrics/support | Fintech | **Remote (URL):** https://api.dashboard.plaid.com/mcp/sse |
| 40 | **Sentry (Remote)** | Errors/perf | Eng/SRE | **Remote (URL):** https://mcp.sentry.dev/sse |
| 41 | **Slack (Remote)** | Channels/DMs/files | Eng/Support | **Remote (Directory):** https://claude.ai/directory/597f662f-36de-437e-836e-5a81013cbfbe |
| 42 | **Square (Remote)** | Payments data | Commerce | **Remote (URL):** https://mcp.squareup.com/sse |
| 43 | **Zapier (Remote)** | Automations (thousands of apps) | Ops | **Remote (Guide):** https://mcp.zapier.com/ |
| 44 | **Vercel (Remote)** | Deploys/logs/env | Frontend/Platform | **Remote (Guide):** https://vercel.com/docs/mcp/vercel-mcp  (Endpoint: https://mcp.vercel.com) |
| 45 | **Browserbase (Remote)** | Hosted browsers | QA/Growth | **Remote (Guide):** https://docs.browserbase.com/integrations/mcp/setup |
| 46 | **Stripe (Remote)** | Billing/payments | Fintech | **Remote (Guide):** https://docs.stripe.com/mcp  (Endpoint: https://mcp.stripe.com) |
| 47 | **Notion (Alt OSS Remote)** | Community server variant | Builders | **Remote (Guide):** https://github.com/makenotion/notion-mcp-server |
| 48 | **CData Connect AI (Remote)** | Data connectors hub | Data/IT | **Remote (Guide):** https://www.cdata.com/kb/tech/googledrive-cloud-claude.rst (Drive example; URL: https://mcp.cloud.cdata.com/mcp) |
| 49 | **CData Connect AI (Calendar)** | Google Calendar via CData | PM/EM | **Remote (Guide):** https://www.cdata.com/kb/tech/googlecalendar-cloud-claude.rst |
| 50 | **Context7 (Remote URL)** | Hosted endpoint | All devs | **Remote (URL):** https://mcp.context7.com/mcp |
| 51 | Google Drive (local alt) | Drive/Docs (community) | Everyone | `claude mcp add gdrive -- npx -y jasonwong/google-drive-mcp` *(example OSS; swap to your preferred)* |
| 52 | Gmail (local alt) | Mail ops (community) | Ops | `claude mcp add gmail -- npx -y tjzaks/gmail-mcp-server` |
| 53 | Google Calendar (local alt) | Events ops (community) | PM/EM | `claude mcp add gcal -- npx -y jackson88/google-calendar-mcp` |
| 54 | BigQuery | Warehouse queries | Data | `claude mcp add bigquery -- npx -y mcp-bigquery-server` |
| 55 | Snowflake | Warehousing | Data | `claude mcp add snowflake -- npx -y mcp-snowflake-server` |
| 56 | Neo4j | Graph (Cypher) | Graph/Data Sci | `claude mcp add neo4j -- npx -y mcp-neo4j-server` |
| 57 | Weights & Biases (Remote) | ML tracking | MLOps | **Remote (Directory):** https://claude.ai/directory |
| 58 | MLflow | Experiments/artifacts | MLOps | `claude mcp add mlflow -- npx -y mcp-mlflow-server` |
| 59 | Airflow | DAG ops | Data Eng | `claude mcp add airflow -- npx -y mcp-airflow-server` |
| 60 | Dagster | Jobs/assets | Data Eng | `claude mcp add dagster -- npx -y mcp-dagster-server` |
| 61 | Jenkins | CI jobs/builds | DevOps | `claude mcp add jenkins -- npx -y mcp-jenkins-server` |
| 62 | GitHub Actions | Workflows/runs | DevOps | `claude mcp add gha -- npx -y @modelcontextprotocol/server-github-actions` |
| 63 | S3 | Buckets/objects | Platform/Data | `claude mcp add s3 -- npx -y mcp-s3-server` |
| 64 | GCS | Google Cloud Storage | Platform | `claude mcp add gcs -- npx -y mcp-gcs-server` |
| 65 | Azure Blob | Blob storage | Platform | `claude mcp add azure-blob -- npx -y mcp-azure-blob-server` |
| 66 | Cloud Run (deploy tool) | Deploy MCPs to Cloud Run | Platform | **Remote (Guide):** https://cloud.google.com/run/docs/host-mcp-servers |
| 67 | Cloud Run (sample server) | Deploy apps via MCP | Platform | **Remote (Guide):** https://github.com/GoogleCloudPlatform/cloud-run-mcp |
| 68 | OpenAI | API utilities | AI Eng | `claude mcp add openai -- npx -y @mcp-labs/openai-mcp` |
| 69 | Anthropic | API utilities | AI Eng | `claude mcp add anthropic -- npx -y @mcp-labs/anthropic-mcp` |
| 70 | Ollama | Local models/embeddings | AI Eng | `claude mcp add ollama -- npx -y @mcp-labs/ollama-mcp` |
| 71 | Hugging Face | Models/datasets ops | AI Eng | `claude mcp add huggingface -- npx -y mcp-hf-server` |
| 72 | Langfuse (Remote) | LLM tracing | AI/MLOps | **Remote (Directory):** https://claude.ai/directory |
| 73 | ServiceNow (Remote) | Tickets/CMDB | ITSM | **Remote (Directory):** https://claude.ai/directory |
| 74 | PostHog (Remote) | Product analytics | Growth/Eng | **Remote (Directory):** https://claude.ai/directory |
| 75 | Twilio (Remote) | SMS/voice/email | Ops/Growth | **Remote (Directory):** https://claude.ai/directory |
| 76 | SendGrid (Remote) | Transactional email | Growth | **Remote (Directory):** https://claude.ai/directory |
| 77 | Postmark (Remote) | Transactional email | Growth | **Remote (Directory):** https://claude.ai/directory |
| 78 | PagerDuty (Remote) | Incidents/on-call | SRE | **Remote (Directory):** https://claude.ai/directory |
| 79 | Opsgenie (Remote) | Alerts/on-call | SRE | **Remote (Directory):** https://claude.ai/directory |
| 80 | Splunk (Remote) | SPL/search/dashboards | SecOps/SRE | **Remote (Directory):** https://claude.ai/directory |
| 81 | Grafana (Remote) | Dashboards/Loki/Tempo | SRE | **Remote (Directory):** https://claude.ai/directory |
| 82 | Prometheus (local) | Metrics queries | SRE | `claude mcp add prometheus -- npx -y @mcp-labs/prometheus-mcp` |
| 83 | Supabase (Remote) | Auth/Postgres/Storage | App/Data | **Remote (Directory):** https://claude.ai/directory |
| 84 | Netlify (Remote) | Sites/deploys | Frontend | **Remote (Directory):** https://claude.ai/directory |
| 85 | Cloudflare (local alt) | Local runner | Platform | `claude mcp add cloudflare-local -- npx -y cloudflare/mcp-server-cloudflare` |
| 86 | Browserbase (local alt) | Local/SHTTP variant | QA/Growth | `claude mcp add browserbase -- npx -y browserbase/mcp-server-browserbase` |
| 87 | Stripe (OSS alt) | Agent toolkit | Fintech | **Remote (Guide):** https://www.pulsemcp.com/servers/stripe-agent-toolkit |
| 88 | ICS/Calendar | Parse/merge ICS | PM/EM | `claude mcp add ics -- npx -y mcp-ics-server` |
| 89 | CSV/Parquet | Inspect/transform | Data | `claude mcp add parquet -- npx -y mcp-parquet-server` |
| 90 | Obsidian | PKM vault | Docs/PKM | `claude mcp add obsidian -- npx -y mcp-obsidian-server` |
| 91 | MediaWiki | Query/edit wiki | Docs/Research | `claude mcp add mediawiki -- npx -y mcp-mediawiki-server` |
| 92 | Wikipedia/OpenLibrary | Encyclo/books search | Research | `claude mcp add openlibrary -- npx -y mcp-open-library` |
| 93 | NVD Advisories | CVE lookup/enrich | SecEng | `claude mcp add nvd -- npx -y mcp-nvd-server` |
| 94 | Vault | Secrets (KV/Transit) | Sec/Platform | `claude mcp add vault -- npx -y @mcp-labs/vault-mcp` |
| 95 | 1Password | Secrets retrieval | Eng/Sec | `claude mcp add 1password -- npx -y @mcp-labs/1password-mcp` |
| 96 | Doppler | Secrets mgmt | Eng/Sec | `claude mcp add doppler -- npx -y @dopplerhq/mcp-server` |
| 97 | Jenkins (Remote alt) | OAuth remote variant | DevOps | **Remote (Guide):** https://claude.ai/directory |
| 98 | Chrome DevTools (Remote) | Headless control APIs | QA/Perf | **Remote (Directory):** https://claude.ai/directory |
| 99 | Memory (Unified) | Long-term semantic memory | Any dev | `claude mcp add memory -- npx -y mcp-memory-service` |
| 100 | PulseMCP Discovery | Find/install MCPs fast | Power users | `claude mcp add pulsemcp -- npx -y @orliesaurus/pulsemcp-server` |

