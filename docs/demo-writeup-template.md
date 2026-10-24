# AutoForge end-to-end demo: <date>

<!--
Template for the write-up of one demo run (iceboundrock/AutoForge#261).
Fill it from the excerpts that passed the redaction review (docs/RUNBOOK.md,
section 11) and from GitHub, never from memory. Every claim links to a GitHub
artifact or to a published trace excerpt. Write what happened, including
failures and retries, in the order they happened. Delete these comments.
-->

## Summary

<One paragraph: AutoForge `<commit>` took issue <issue link> of
`iceboundrock/autoforge-demo` through implementation (Claude Code), an
independent review (OpenCode) <and one fix iteration | and no fix: the first
review was clean>, and stopped at `READY_FOR_MERGE` on PR <PR link> after
<n> review round(s) and <hh:mm> of wall-clock time. The merge gate was closed;
<the maintainer merged the PR on <date> | the PR was not merged>.>

| | |
|---|---|
| AutoForge commit | `<40-character SHA>` |
| Demo repository at the start | `demo-start` = `<SHA>` |
| EPIC, issue | <EPIC link>, <issue link> |
| Pull request | <PR link> |
| Final phase | `READY_FOR_MERGE` <or the phase and reason> |
| Review rounds | <n> |
| Fix iterations claimed | <n, or "none"> (see [Fix iteration](#fix-iteration-requirement-7)) |
| Wall-clock, whole run | <hh:mm:ss> (`created_at` to `updated_at` of the final state) |
| Human actions | <n>, listed in [Human actions](#human-actions-requirement-5) |

## Configuration and versions (Requirement 3)

The configuration is [`autoforge.demo.yaml` at `demo-start`](<link to the file at the tag>),
SHA-256 `<sha256>`, unchanged during the run (`sha256sum -c` after it: OK).

| Phase | Profile | Provider | Model (configured) | Model (as the trace reports it) | Effort | Idle timeout / ceiling |
|---|---|---|---|---|---|---|
| ANALYZE_EXECUTE | `analyze_execute` | claude | `fable` | `<from models.txt>` | high | 900 s / 2700 s |
| REVIEW round 1 | `review_round_1` | opencode | `openai/gpt-5.6-luna` | `openai/gpt-5.6-luna` | high | 900 s / 1800 s |
| FIX | `fix` | claude | `fable` | `<...>` | high | 900 s / 1800 s |
| REVIEW rounds 2-3 | `review_round_2_5` | opencode | `openai/gpt-5.6-terra` | `openai/gpt-5.6-terra` | high | 900 s / 1800 s |

<Delete the rows of profiles the run did not use; say which were not used.>

| Component | Version | Source |
|---|---|---|
| AutoForge | `<autoforge --version>`, commit `<SHA>` | install route <A / B / C> (docs/RUNBOOK.md, section 3)<; #259's guide had / had not landed> |
| gh | `<...>` | `doctor`: `gh available` |
| git | `<...>` | `doctor`: `git available` |
| Claude Code | `<...>` | `doctor`: `agent 'claude' available (...)` |
| OpenCode | `<...>` | `doctor`: `agent 'opencode' available (...)` |
| Python | `<...>` (AutoForge's tool environment; the validation commands use `uvx --python 3.12`) | `uv tool list --show-python` |
| uv | `<...>` | `uv --version` |
| OS | `<NAME VERSION, kernel>` | `/etc/os-release`, `uname -srm` |
| `sandbox.mode` | `<disabled / required>` | `autoforge.demo.yaml`; `doctor`: `outer sandbox: mode (...)` |

Doctor rows that were not OK, and why: <the expected `WARN outer sandbox:
mode (disabled)` and `SKIP default branch requires checks` (the token cannot
read bypass actors; the admin read below shows none), and anything else>.

## Artifacts (Requirement 4)

- Issue: <link>. EPIC: <link>. Both filed by the maintainer.
- Pull request: <link>, opened by AutoForge on `autoforge/<issue>`.
- Commits (from the PR):

  | Commit | Author | Message | Produced in step |
  |---|---|---|---|
  | `<short SHA>` | <author as git records it> | <subject> | <seq>-analyze_execute-<attempt> |

- Review comments posted by AutoForge from the reviewer's result:

  | Round | Comment | Result | Findings | Reviewed HEAD |
  |---|---|---|---|---|
  | 1 | <link> | <needs_fix / clean> | <n> | `<short SHA>` |

- Trace excerpt, redacted: the phase sequence (`[<run-id>] <PHASE> -> <NEXT>: ...`
  lines of the run's console output), the per-invocation table
  (`steps.tsv`) and `status --json` at the end, reduced to the fields in
  docs/RUNBOOK.md section 11:

  ```text
  <transitions.txt>
  ```

  ```json
  <publish/status.json>
  ```

## Human actions (Requirement 5)

Everything a human did. Everything else was done by AutoForge or by the
agents it launched.

| # | Time (UTC) | Who | Action | Command or UI | Why | Artifact or trace reference |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

## Timings and outcomes (Requirement 6)

| Step | Phase | Attempt | Profile | Model | Started (UTC) | Finished (UTC) | Duration | Ended by / exit |
|---|---|---|---|---|---|---|---|---|
| <seq> | <phase> | <n> | <profile or "controller validation"> | <model> | | | <mm:ss> | <exit 0> |

- Wall-clock per phase: ANALYZE_EXECUTE <...>, REVIEW <...> (round 1),
  FIX <...>, REVIEW <...> (round 2); whole run <...>, of which the
  controller's own work (validation, pushes, GitHub reads) <...>.
- Review rounds: <n>. Steps counted against `workflow.max_total_steps: 20`:
  <step_count>.
- Failures, retries and recoveries, as they happened: <"none", or each one:
  what failed (the error or limit as printed), what the controller did,
  what the maintainer did (with the human-action number), and the step it
  continued from>.

## Fix iteration (Requirement 7)

<Exactly one of the two paragraphs below.>

**Claimed.** The trace shows `REVIEW` round <n> with <k> finding(s)
(<comment link>, `review_history` entry `{"round": <n>, "result": "needs_fix",
"finding_count": <k>}`), then `FIX` (step <seq>, commit <link>), then a clean
`REVIEW` round <n+1> (<comment link>, `"result": "clean"`).

**Not claimed.** The first review was clean (<comment link>); this run is
published as a clean run. <Either: "A second, staged run is described in
<link>." or: "No fix iteration is claimed.">

**Staging, disclosed.** The demo issue was written so that a review finding
is plausible: it requires full Unicode case folding (`str.casefold()`, under
which `Straße` and `STRASSE` are one word, unlike with `str.lower()`), ties
ordered by the word rather than by first appearance (unlike
`collections.Counter.most_common`), and no output at all for an input
without words. These requirements are stated explicitly in the issue and its
test list; the issue does not mention that it is staged, and nothing else
about the run was arranged.

## Reproducing it (Requirement 8)

On your own fork, with your own credentials: [docs/RUNBOOK.md, section 14](<link>).
Expect different code, findings and timings; the phase sequence is what
reproduces. Use AutoForge `<commit>` and `autoforge.demo.yaml` at `demo-start`.

## Cost and limits (Requirement 9)

| Provider | Billing | Provider-side limit | Planned | Reported after the run |
|---|---|---|---|---|
| Claude Code | <subscription / API (Console)> | <limit and where, or "subscription: none"> | <budget, or "n/a: subscription"> | <tokens and cost the provider reported, or invocations, total duration and any usage-limit hit> |
| OpenCode (OpenAI) | <ChatGPT sign-in / API key> | <...> | <...> | <...> |

- Agent invocations: <n> (Claude Code <n>, OpenCode <n>), total agent time
  <...>; whole run <...>.
- Subscription quota is reported separately from API spend, and no dollar
  figure is given for a subscription. <If quoted at all: Claude Code's own
  `total_cost_usd` estimate under a subscription was <...>; it is not a
  charge.>
- The controller's bounds, which held for the whole run: review rounds 3,
  correction attempts 1, step budget 20, per-profile idle timeout 900 s and
  ceilings 45 min (implement) and 30 min (fix, review). <Say whether any
  fired.>

## Containment (Requirement 2)

- **Interaction limits:** `collaborators_only` from <time> to <time> (UTC),
  set and lifted with `gh api .../interaction-limits`; <GET output before the
  run>.
- **Environment:** <a dedicated OS user / VM / container> holding no other
  credential; `sandbox.mode: <disabled>`. <Under `disabled`: "No launch ran
  inside the outer sandbox: agents and validation commands ran as the demo
  user with logical isolation only (their own worktree, an allow-listed
  environment without a GitHub or git credential)." Never call such a run
  sandboxed.>
- **GitHub token:** fine-grained, `iceboundrock/autoforge-demo` only,
  Metadata read, Contents read and write, Pull requests read and write,
  Issues read and write, Commit statuses read; expiry <date>; revoked on
  <date>.
- **Branch rules:** ruleset <name> (#<id>) on `main`, `active`, no bypass
  actors, requiring a pull request and the `ci` check (the admin read of the
  ruleset, published as <link>).
- **Model credentials:** <as in Cost and limits>.

## Redaction review

The published excerpts (<list of files>) were reviewed by <who> on <date,
UTC>: terminal escapes stripped, the credential-shape and personal-data
searches of docs/RUNBOOK.md section 11 run with no unexplained hit, and every
line read. State files and raw logs were not published.

## Acceptance criteria of #261

- [ ] Every phase claimed above is traceable to a GitHub artifact and to the
  run trace: <where>.
- [ ] Configuration, versions and AutoForge commit stated; staging
  disclosed; human actions listed separately.
- [ ] A fix iteration is claimed only if the trace shows it.
- [ ] Published excerpts reviewed for secrets and personal data:
  [Redaction review](#redaction-review).
- [ ] The run was contained (interaction limits, dedicated environment,
  scoped token, spend-limited or subscription-bounded models), and this
  write-up says how: [Containment](#containment-requirement-2).
- [ ] The reproduction procedure exists:
  [Reproducing it](#reproducing-it-requirement-8).
- [ ] Gate 3: at the release candidate, the demo was re-run on the RC, or the
  maintainer recorded on #255 why no change since `<commit>` affects it:
  <link, filled in at the RC>.
