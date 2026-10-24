# Demo runbook

How the maintainer runs AutoForge's end-to-end demo on this repository
([iceboundrock/AutoForge#261](https://github.com/iceboundrock/AutoForge/issues/261)),
keeps the evidence, and how someone else reproduces it on a fork. It follows
the maintainer's decision on #261
([comment](https://github.com/iceboundrock/AutoForge/issues/261#issuecomment-6377402317)):
a real run, merge gate closed, a human merges, nothing a human edited is
presented as AutoForge's output, and no paid model call before the
maintainer has authorized it with provider-side limits in place.

The commands below were checked against AutoForge `12e10f4` (its `--help`,
`docs/usage.md`, `docs/configuration.md`, `docs/security.md`), gh 2.102.1 and
GitHub's REST documentation. Where AutoForge has moved on by the time of the
run, the AutoForge commit you install is the reference: check each command
against its `--help` again.

Conventions:

- `$EV` is an evidence directory outside every checkout
  (`mkdir -p ~/evidence && EV=~/evidence`), in the maintainer's shell and in
  the demo user's; keep the two sets together. Everything in it is raw and
  private until section 11 has been done.
- Placeholders are in angle brackets. `$EPIC`, `$ISSUE`, `$EPIC_URL` and
  `$ISSUE_URL` are set in section 5 (maintainer) and section 7 (demo user).
- Commands are bash. "As the maintainer" means your own account's `gh`
  login, which administers the repository; everything else runs as the
  dedicated demo user with the demo token only.

## 0. Decisions to record before you start

Write these into `$EV/decisions.md`; the write-up repeats them.

| Decision | Options | Notes |
|---|---|---|
| AutoForge commit | a full 40-character SHA of `iceboundrock/AutoForge` | The commit the write-up names. Prefer one where #256's packaging fix and #259's install guide have landed. |
| Install route | section 3 A, B or C | Requirement 1 says "installed the way #259's guide says"; if #259 has not landed, say so and name the route. |
| Claude Code billing | Claude subscription login, or Anthropic Console (API) | Decides what section 6 records. |
| OpenCode (OpenAI) billing | ChatGPT sign-in, or OpenAI API key | Same. |
| Planned budget | per API-billed provider | Only for API billing; never invented for a subscription. |
| `sandbox.mode` | `disabled` (as committed), or `required` | `required` only where `autoforge doctor` reports the outer sandbox capability as supported, and only with OpenCode's login reachable inside it (section 1). A change to `autoforge.demo.yaml` is a commit to this repository before the run. |
| Git identity of agent commits | a name and email for the demo user | Agents commit with the author identity of the user that runs AutoForge. |
| Merge afterwards | yes or no | A human merge is listed as a human action. If you merge, the reproduction uses the `demo-start` tag (section 14). |

## 1. Containment: the environment

Run the demo as a dedicated OS user (or in a VM or container) that holds
nothing but what the demo needs:

```bash
sudo useradd --create-home --shell /bin/bash afdemo
sudo -iu afdemo
```

That user has:

- no SSH key, no `~/.netrc`, no other `gh` login, no cloud or other API
  credential, and no credential exported from a shell startup file
  (`~/.bash_profile`, `~/.bashrc`, `~/.profile`); AutoForge refuses a launch
  whose login shell would hand an agent `GH_TOKEN`, and a startup file would
  also persist it;
- no `GEMINI_*`, `GOOGLE_*` or `AWS_*` variable in its environment: OpenCode
  launches receive `GEMINI_*` and `GOOGLE_*`, and AutoForge does not redact
  every key shape (#282, #285);
- never `gh auth setup-git`: AutoForge hands the token to git itself
  (`gh auth git-credential`) for its own fetches and pushes;
- a git identity, which the agents' commits carry:

  ```bash
  git config --global user.name "<name>"
  git config --global user.email "<email>"
  ```

What this does and does not protect, stated the way the write-up must state
it: with `sandbox.mode: disabled` (the committed setting) every agent and
every validation command runs as this user with logical isolation only (its
own worktree, an allow-listed environment without a GitHub or git
credential). It is **not sandboxed**: an agent that goes looking can read
what this user can, the demo token in the controller's environment and the
model logins included. The containment is therefore that this user holds
nothing else, that the token can do little and expires soon (section 4), that
the model logins are spend-limited or subscription-bounded (section 6), and
that only collaborators can write on the repository while a run is active
(section 5).

`sandbox.mode: required` is stronger where it works: on a host where
`autoforge doctor` shows `outer sandbox: capability (...): supported`, every
launch runs inside the outer sandbox and its record says `enforced: true`.
Inside it OpenCode cannot reach its usual login in `~/.local/share/opencode`
(give it an absolute `OPENCODE_DB` outside that directory and run `opencode
auth login` with it set, or use `OPENAI_API_KEY`), and Claude Code's login is
visible read-only, so a subscription token cannot be refreshed (give it a
dedicated `CLAUDE_CONFIG_DIR` and log in once with it set, or
`CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`); see
`docs/configuration.md`, "Outer sandbox". Decide before the run; never
describe a run under `disabled` as sandboxed.

## 2. Tools and the versions to record

As the demo user, install: git, gh (2.48.0 or newer), uv, Claude Code and
OpenCode (2.0.0 or newer), each the way its own documentation says. Python
3.12 is provided by uv. Then record:

```bash
mkdir -p ~/evidence && EV=~/evidence
{
  echo "recorded: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  grep -E '^(NAME|VERSION)=' /etc/os-release
  uname -srm
  git --version
  gh --version | head -n 1
  uv --version
  uv run --no-project --python 3.12 python --version
  claude --version
  opencode --version
} > "$EV/versions.txt"
```

After section 3, append AutoForge's:

```bash
{
  autoforge --version
  uv tool list --show-version-specifiers --show-python
  echo "AutoForge commit: <commit>"
} >> "$EV/versions.txt"
```

`autoforge --version` prints the package version only, not the commit, so
the commit is recorded from the install (section 3). Requirement 3 asks for
the versions "as `doctor` reports them": the `gh available`, `git available`,
`agent 'claude' available (...)` and `agent 'opencode' available (...)` rows
of `$EV/doctor.json` (section 7) are the ones the write-up quotes.

## 3. Install AutoForge at the named commit

Use one route and record it.

**A. From GitHub at the commit** (until the first PyPI release, #295, and
#259's guide):

```bash
uv tool install --python 3.12 git+https://github.com/iceboundrock/AutoForge@<commit>
```

Only for a commit whose built package contains the prompt templates
(#256). At `12e10f4` it does not: a wheel built from `12e10f4` and installed
with `uv tool install` fails the first dry run with
`autoforge: error: prompt template missing: .../site-packages/autoforge/prompts/acceptance_actions.md`
(exit 2). The `git+https` form builds the package the same way, so expect
the same failure from it at that commit (not tried). Whatever the commit, the
dry run of section 7 must exit 0 before anything else runs.

**B. Editable, from a checkout at the commit** (works at `12e10f4`):

```bash
git clone https://github.com/iceboundrock/AutoForge.git ~/src/AutoForge
git -C ~/src/AutoForge checkout --detach <commit>
uv tool install --python 3.12 --editable ~/src/AutoForge
git -C ~/src/AutoForge rev-parse HEAD >> "$EV/versions.txt"
git -C ~/src/AutoForge status --short     # must print nothing
```

The installed command runs the code in `~/src/AutoForge`: do not edit, pull
or switch it until the run is over, and repeat the last two commands after
the run (section 8) to show it did not change.

**C. From PyPI, after #295:**

```bash
uv tool install --python 3.12 autoforge-cli==<version>
```

The distribution is renamed `autoforge-cli` (#256, #295). The PyPI project
`autoforge` is unrelated: never install it.

AutoForge reads `autoforge.demo.yaml` with PyYAML when it is installed and
with its own YAML subset parser otherwise; for this file both give the same
configuration (checked when the file was written).

## 4. The GitHub token

Create it after the repository exists (section 5), as the maintainer, at
<https://github.com/settings/personal-access-tokens/new> (fine-grained):

- **Name:** `autoforge-demo run <date>`.
- **Expiration:** the shortest that covers the run and the evidence
  collection, for example 7 days.
- **Resource owner:** `iceboundrock`. **Repository access:** only select
  repositories, `iceboundrock/autoforge-demo`.
- **Repository permissions**, exactly those `docs/security.md` lists for
  the merge gate closed:

  | Permission | Access | Why |
  |---|---|---|
  | Metadata | Read | every fine-grained token; the repository and its default branch |
  | Contents | Read and write | fetching; pushing `autoforge/<issue>` (never `main`); comparing branches |
  | Pull requests | Read and write | opening the PR; the review comment |
  | Issues | Read and write | reading the issue, the EPIC and their comments; a FIX's follow-up issue or acceptance comment |
  | Commit statuses | Read | legacy commit statuses in the PR head's check results |

  Nothing else: no Actions (needed only by an open merge gate), no
  Workflows (without it GitHub refuses a push that changes
  `.github/workflows/`, and the run blocks), no Administration, no account
  permissions. A fine-grained token has no Checks permission; on a public
  repository the check runs are readable without one (#291 affects private
  repositories only).

Hand it to the demo user's shell, and only to that shell:

```bash
read -rs GH_TOKEN && export GH_TOKEN    # paste it; nothing is echoed
gh auth status                          # names the account and GH_TOKEN as the source
```

Never put it on a command line, in a file, in a shell startup file, in
`autoforge.demo.yaml` or in `execution.env_allowlist_extra` (AutoForge
refuses that), and never run `gh auth status --show-token` or `gh auth
token`. Do not save `gh auth status` output as evidence. The token lives as
long as that shell: open a new shell and read it again to resume later. In a
VM or container instead of a dedicated user, the same applies; on your own
OS user a separate `GH_CONFIG_DIR` keeps a stored login apart, but your
other credentials stay within the agents' reach, which is what section 1
avoids.

Revoke the token at <https://github.com/settings/personal-access-tokens>
once section 10's evidence is collected and no `resume` is planned.

## 5. The repository, its settings, the EPIC and the issue

As the maintainer, from this prepared repository:

```bash
gh repo create iceboundrock/autoforge-demo --public \
  --description "Demonstration of AutoForge: a GitHub issue to an independently reviewed PR, ready for human merge" \
  --disable-wiki --source . --remote origin --push
git tag -a demo-start -m "State of the repository when the demo run started"
git push origin demo-start
```

Wait for the first CI run on `main` and check it passed (the `push` run of
`main` is also what AutoForge compares a PR's checks against):

```bash
gh run list -R iceboundrock/autoforge-demo --branch main --event push --limit 1 \
  --json databaseId,headSha,status,conclusion
gh run watch -R iceboundrock/autoforge-demo <databaseId> --exit-status
```

Read-only `GITHUB_TOKEN` for workflows, no PR approvals by workflows (the
workflow file already asks for `contents: read` only):

```bash
gh api -X PUT repos/iceboundrock/autoforge-demo/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
gh api repos/iceboundrock/autoforge-demo/actions/permissions/workflow
```

The ruleset on `main`: a pull request is required (squash only, no
approval count, since the merge gate is closed and you merge), the `ci`
check from GitHub Actions is required, no deletion, no force push, and no
bypass actor. Its definition is [`docs/ruleset-main.json`](ruleset-main.json)
(`integration_id` 15368 is the GitHub Actions app):

```bash
gh api -X POST repos/iceboundrock/autoforge-demo/rulesets --input docs/ruleset-main.json --jq .id
gh api repos/iceboundrock/autoforge-demo/rulesets/<id> \
  --jq '{id, name, enforcement, bypass_actors, rules: [.rules[].type]}' > "$EV/ruleset.json"
gh api repos/iceboundrock/autoforge-demo/rules/branches/main --jq '[.[].type]'
```

`ruleset.json` must show `"enforcement": "active"` and `"bypass_actors": []`.
This admin read is the evidence that nobody can bypass the rule: the demo
token cannot see bypass actors, so `doctor` skips that part (section 7).

Interaction limits, collaborators only, before the EPIC and the issue exist
and for as long as a run is active (owner or admin only; the expiry is one
of `one_day`, `three_days`, `one_week`, `one_month`, `six_months`):

```bash
gh api -X PUT repos/iceboundrock/autoforge-demo/interaction-limits \
  -f limit=collaborators_only -f expiry=one_week
gh api repos/iceboundrock/autoforge-demo/interaction-limits > "$EV/interaction-limits-set.json"
```

File the EPIC and the issue from [`issues/`](../issues/); the issue becomes a
sub-issue of the EPIC:

```bash
EPIC_URL=$(gh issue create -R iceboundrock/autoforge-demo \
  --title "Demo EPIC: wordstat features built by AutoForge" --body-file issues/epic.md)
EPIC=${EPIC_URL##*/}
ISSUE_URL=$(sed "s/{{EPIC_NUMBER}}/$EPIC/" issues/001-top-words.md | \
  gh issue create -R iceboundrock/autoforge-demo \
  --title 'Add a `--top N` option that lists the most frequent words' \
  --body-file - --parent "$EPIC")
ISSUE=${ISSUE_URL##*/}
echo "$EPIC_URL $ISSUE_URL" > "$EV/issues.txt"
```

Then create the token (section 4).

## 6. Model spend

No fixed dollar cap. The limits come from how each provider is billed and
from what the run calls; a budget written in a prompt is not a limit, and
AutoForge sees no money.

Log in as the demo user, with the billing type decided in section 0:

- Claude Code: `claude auth login` (Claude subscription, the default) or
  `claude auth login --console` (Anthropic Console, API usage billing).
- OpenCode: `opencode auth login`, choosing OpenAI with a ChatGPT sign-in or
  an API key.

**For an API-billed provider,** before the run:

- set a real spend limit on the provider's side for the key the run uses
  (a dedicated workspace or project for the demo makes it the run's own),
  and write down whether the provider enforces it or only notifies;
- record the planned budget in `$EV/spend-plan.md`.

After the run, record the token and cost figures the provider's usage page
reports for that key and the run's time window.

**For a subscription login,** no dollar figure is invented. The run's bounds
are the controller's (`autoforge.demo.yaml`: per-profile idle timeout and
ceiling, `workflow.max_review_rounds: 3`,
`execution.max_correction_attempts: 1`, `workflow.max_total_steps: 20`).
Record the number of agent invocations, their durations, and any
subscription usage limit that was hit (section 10). Subscription quota used
is reported separately from API spend. Claude Code's result carries a
`total_cost_usd` (AutoForge keeps it as `cost_micro_usd`); under a
subscription it is Claude Code's estimate, not a charge, and is not reported
as spend.

**Authorization.** `doctor` and `--dry-run` make no model call. The first
paid call is `run` in section 8. Before it, write into `$EV/spend-plan.md`
the billing type per provider, each limit and where it is set, the planned
budget, and the maintainer's authorization with the date and time (UTC).

## 7. Preflight

As the demo user, with `GH_TOKEN` set (section 4):

```bash
git clone https://github.com/iceboundrock/autoforge-demo.git ~/autoforge-demo
cd ~/autoforge-demo
git remote get-url origin                 # https://github.com/iceboundrock/autoforge-demo.git
git rev-parse HEAD 'demo-start^{commit}'  # the same commit twice
EPIC=<n>; ISSUE=<n>
EPIC_URL=https://github.com/iceboundrock/autoforge-demo/issues/$EPIC
ISSUE_URL=https://github.com/iceboundrock/autoforge-demo/issues/$ISSUE
af() { autoforge --config autoforge.demo.yaml --state-dir ".autoforge/issue-$ISSUE" "$@"; }
sha256sum autoforge.demo.yaml > "$EV/config.sha256"
```

`af` only saves typing: every command passes the configuration and the
run's state directory before the subcommand, and `resume`, `status` and
`unblock` must pass the same two (`.autoforge/` is gitignored). Write the
full command in the human-actions list.

```bash
af doctor
af doctor --json > "$EV/doctor.json"
```

Expected: no required row fails (`doctor --json` reports `"ok": true`; the
exit status is 1 when a required row fails). Two rows are expected not to
be OK, and the write-up says why:

- `[WARN] outer sandbox: mode (disabled): logical isolation only ...`, under
  the committed `sandbox.mode: disabled`;
- `[SKIP] default branch requires checks: 'main' requires: ci via ruleset
  #<id> ...; bypass actors ... are not visible to this token`: the
  fine-grained token cannot read bypass actors; `$EV/ruleset.json` (section
  5) shows there are none. A FAIL here (a missing `ci`, a ruleset not
  `active`, a bypass actor) stops the demo until the ruleset is fixed.

Any other FAIL stops the demo. Then the dry run, which starts no process,
makes no `gh` call and writes no file (checked for this configuration with
a stub `gh`, `git` and agent CLIs that recorded no invocation):

```bash
af run --epic "$EPIC_URL" --issue "$ISSUE_URL" --dry-run > "$EV/dry-run.txt"
```

It must exit 0 and show `INITIALIZING`, then `ANALYZE_EXECUTE` with
`Profile:  analyze_execute (provider=claude, model=fable, effort=high)`,
`Limits:   idle timeout 900s, max runtime 2700s`, the three candidate
validation definitions and `REPOSITORY = iceboundrock/autoforge-demo`.

Last check before the paid call: the interaction limit is still in force
(as the maintainer, `gh api repos/iceboundrock/autoforge-demo/interaction-limits`
shows `"limit": "collaborators_only"` and an `expires_at` after the run's
expected end), and `$EV/spend-plan.md` holds the authorization (section 6).

## 8. The run

Start it in `tmux` or `screen`, so a dropped terminal does not end it. After
a closed laptop, `Ctrl-C` or a killed process, `af resume` (in a shell with
`GH_TOKEN`, `ISSUE` and `af` set again) continues from the persisted state,
or the run enters `BLOCKED` with a reason when recovery cannot tell the safe
state; either is reported as it happened.

```bash
set -o pipefail
af run --epic "$EPIC_URL" --issue "$ISSUE_URL" 2>&1 | tee "$EV/run-console.txt"; echo "exit $?"
```

Progress lines (stderr) look like `[00:00:04 ANALYZE_EXECUTE #<issue>] agent
started (<model>)`; each step's outcome (stdout) is one line
`[<run-id>] <PHASE> -> <NEXT>: <message>`. From another terminal:

```bash
cd ~/autoforge-demo && ISSUE=<n>
af() { autoforge --config autoforge.demo.yaml --state-dir ".autoforge/issue-$ISSUE" "$@"; }
af status                                 # takes no lock; safe while the run is active
RUN_ID=$(af status --json | jq -r .run_id)
ls ".autoforge/issue-$ISSUE/logs/$RUN_ID/"
tail -f ".autoforge/issue-$ISSUE/logs/$RUN_ID/<seq>-<phase>-<attempt>/progress.log"
```

The run ends in one of these:

- **`READY_FOR_MERGE`** (exit 0): a banner with the issue, the PR, the review
  round, the reviewed HEAD, the review certificate and `Automatic merge is
  disabled in this milestone.` This is the end of AutoForge's part.
- **An agent failure or a limit** (non-zero exit, an error naming the limit
  or failure, the phase unchanged, nothing retried): read the error and the
  step's `execution.json`, then decide whether to continue:
  `af resume 2>&1 | tee -a "$EV/run-console.txt"`. `resume` continues the
  same step budget.
- **`BLOCKED`** (exit 1, `run <run-id> is BLOCKED: <reason>`): read
  `af status`, fix the cause on GitHub (the reason says what), then

  ```bash
  af unblock --dry-run --reason "<what you did>"
  af unblock --reason "<what you did>"
  af resume 2>&1 | tee -a "$EV/run-console.txt"
  ```

  Do not raise a bound that fired (review rounds, step budget,
  stagnation) to get past it during the demo: report it as the outcome.
- **A FIX acceptance action** (`safety.acceptance_actions: approve`):
  `af status --action <A-id>` prints the exact comment; approve with
  `af unblock --approve-action <A-id> --reason "<why>"` or decline with
  `af unblock --decline-action <A-id> --reason "<why>"`, then `af resume`.
- **FIX operator actions**: post the comment yourself
  (`af status --action <X-id> | gh issue comment <issue URL> --body-file -`)
  and `af unblock --reason "<what you did>"`, or decline it with
  `af unblock --decline-action <X-id> --reason "<why>"`; then `af resume`.
  See `docs/usage.md`, "BLOCKED on operator actions".

Do not change `autoforge.demo.yaml` during the run. `step`, `resume` and
`unblock` refuse a changed profile routing or worktree root unless
`--accept-config-change` is passed; if you ever pass it, the write-up says
what changed and why.

Every `resume`, `unblock`, approval, comment or other intervention goes into
the human-actions list (section 12) when it happens, with the time.

Afterwards:

```bash
af status > "$EV/status-final.txt"
af status --json > "$EV/status-final.json"
git status --short                                   # nothing
git rev-parse HEAD 'demo-start^{commit}'             # unchanged
sha256sum -c "$EV/config.sha256"                     # OK
git -C ~/src/AutoForge rev-parse HEAD                # route B: the recorded commit
git -C ~/src/AutoForge status --short                # route B: nothing
```

As the maintainer, once no run is active or planned, lift the interaction
limit and record it:

```bash
gh api -X DELETE repos/iceboundrock/autoforge-demo/interaction-limits
gh api repos/iceboundrock/autoforge-demo/interaction-limits   # no limit any more
```

If you merge the PR, merge it yourself after reading it (it is a human
action, and AutoForge's part ended at `READY_FOR_MERGE`), for example
`gh pr merge <PR URL> --squash --match-head-commit <reviewed HEAD>`. Revoke
the token (section 4). The agent worktree
(`.git/autoforge/worktrees/<issue>`) is never removed by AutoForge; remove it
with `git worktree remove` when you no longer need it.

## 9. When round 1 is clean, and the staging

Requirement 7: a fix iteration is claimed only when the trace shows a
`REVIEW` with findings, then `FIX`, then a later clean `REVIEW`. If round 1
is clean, the run is published as a clean run (`INITIALIZING`,
`ANALYZE_EXECUTE`, `REVIEW`, `READY_FOR_MERGE`) and the write-up either
omits the fix claim or discloses a second, separately staged run.

The issue is staged, and the write-up says so in these words or equivalent:

> The demo issue was written so that a review finding is plausible: it
> requires full Unicode case folding (`str.casefold()`, under which `Straße`
> and `STRASSE` are one word, unlike with `str.lower()`), ties ordered by the
> word rather than by first appearance (unlike `collections.Counter.most_common`),
> and no output at all for an input without words. These requirements are
> stated explicitly in the issue and its test list; the issue does not
> mention that it is staged, and nothing else about the run was arranged.

## 10. Evidence to collect

All of it into `$EV`, raw; section 11 decides what is published. With `$RUN_ID`
and `L=".autoforge/issue-$ISSUE/logs/$RUN_ID"`:

| Evidence (#261) | How |
|---|---|
| The issue and the EPIC | `gh issue view "$ISSUE_URL" --json number,url,title,author,createdAt,body,comments > "$EV/issue.json"` (and the same for `$EPIC_URL`) |
| The PR and its history | `PR_URL=$(jq -r .current_pr_url "$EV/status-final.json")`; `gh pr view "$PR_URL" --json number,url,title,author,state,createdAt,baseRefName,headRefName,headRefOid,commits,comments,statusCheckRollup > "$EV/pr.json"` |
| Review comments and fix commits | in `pr.json` (`comments`, `commits`). The controller makes every push to `autoforge/<issue>` and posts every review comment, which carries its review marker (agents hold no GitHub credential); match each commit and comment to a step of the trace |
| `status --json` at the end | `$EV/status-final.json` (section 8) |
| Phase sequence | `grep -E '^\[[^]]+\] [A-Z_]+ -> [A-Z_]+:' "$EV/run-console.txt" > "$EV/transitions.txt"` |
| Timings | the jq command below, into `$EV/steps.tsv`; the run's start and end are `created_at` and `updated_at` in `status-final.json` |
| Model versions | `grep -h 'agent started' "$L"/*/progress.log > "$EV/models.txt"` (Claude Code names its resolved model; OpenCode's is the configured `openai/...` id) |
| Usage, Claude Code | `provider-summaries.jsonl` and `claude-results.jsonl`, the commands below |
| Usage, OpenCode | `opencode stats --standalone --all --models --cost --json > "$EV/opencode-stats.json"` (the demo user ran nothing else) |
| Usage, providers | API billing: the provider's reported tokens and cost; subscription: any usage-limit message, from `run-console.txt` and the step's `execution.json` |
| Containment | `$EV/ruleset.json`, `$EV/interaction-limits-set.json`, the token's permission list (as created), `$EV/doctor.json`, `$EV/decisions.md` |
| Versions and configuration | `$EV/versions.txt`, `$EV/doctor.json`, `autoforge.demo.yaml` at `demo-start`, `$EV/config.sha256` |

Timings, one row per invocation (agents and the controller's validation
commands), with the duration in seconds:

```bash
jq -r 'def t: sub("\\.[0-9]+"; "") | sub("\\+00:00$"; "Z") | fromdateiso8601;
  select((.started_at // "") != "" and (.finished_at // "") != "")
  | [.seq, .phase, .attempt, .correction, .review_round, .profile, .provider, .model,
     .effort, .started_at, .finished_at, ((.finished_at | t) - (.started_at | t)),
     .exit_code, .ended_by] | @tsv' "$L/events.jsonl" > "$EV/steps.tsv"
```

Usage figures per step: AutoForge's provider summary of every agent step
(for Claude Code `num_turns`, `duration_ms` and `cost_micro_usd`), and the
`result` records of Claude Code's own output, which carry its token counts:

```bash
for d in "$L"/*/; do
  if [ -f "$d/execution.json" ]; then
    jq -cs --arg step "$(basename "$d")" \
      '{step: $step, provider: .[0].provider, model: .[0].model,
        provider_summary: .[1].provider_summary}' "$d/request.json" "$d/execution.json"
  fi
done > "$EV/provider-summaries.jsonl"
for d in "$L"/*/; do
  if [ -f "$d/stdout.log" ]; then
    jq -cR --arg step "$(basename "$d")" 'fromjson?
      | select(.type == "result")
      | {step: $step, total_cost_usd, num_turns, duration_ms, usage, modelUsage}' "$d/stdout.log"
  fi
done > "$EV/claude-results.jsonl"
```

## 11. Redaction review, before anything is published

Never publish `state.json`, anything under `.autoforge/` (logs,
`read-context/`, `stdout.log`, `stderr.log`, `prompt.md`), `run-console.txt`,
`dry-run.txt` or `doctor.json` as they are. Publish only excerpts made for the
write-up, each as its own file in `$EV/publish/`, for example:

- `status-final.json` reduced to its fields:

  ```bash
  jq '{controller_version, protocol_version, prompt_version, run_id, repository,
       epic_url, current_issue_url, current_pr_url, current_branch, phase,
       review_round, reviewed_head_sha, last_review_comment_url, last_review_result,
       step_count, created_at, updated_at, block_reason,
       review_history: [.review_history[] | {round, result, finding_count, reviewed_head_sha}],
       unblock_history, review_certificate_status}' "$EV/status-final.json" > "$EV/publish/status.json"
  ```

- `steps.tsv`, `transitions.txt` and `models.txt` as made in section 10 (no
  `command`, `cwd` or `log_dir` column);
- the doctor rows the write-up quotes:
  `jq -r '.checks[] | [.name, (if .skipped then "SKIP" elif .ok then "OK" elif .required then "FAIL" else "WARN" end), .detail] | @tsv' "$EV/doctor.json"`,
  keeping only the rows you quote.

For every file in `$EV/publish/`:

1. Strip terminal escapes (`LC_ALL=C` makes the ranges byte ranges), then
   check that none is left (the count must be 0):

   ```bash
   LC_ALL=C sed -i -E 's/\x1b\[[0-9;?]*[ -/]*[@-~]//g; s/\x1b\][^\x07]*\x07//g' <file>
   grep -c $'\x1b' <file>
   ```

2. Search for credential shapes; this must print nothing:

   ```bash
   LC_ALL=C grep -nE 'github_pat_|gh[opsur]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|xox[abprs]-|glpat-|hf_[A-Za-z0-9]{20,}|gsk_|xai-|npm_[A-Za-z0-9]{20,}|[Aa]uthorization:|Bearer |Basic [A-Za-z0-9+/=]{12,}|_API_KEY|_TOKEN=' <file>
   ```

3. Search for personal data; review every hit:

   ```bash
   grep -nF -e "$HOME" -e /home/ -e /Users/ -e "$(id -un)" -e "$(hostname)" <file>
   ```

   plus any email address other than the noreply addresses on the commits.
4. Read every line yourself. AutoForge's redaction is a baseline, not a
   proof: it misses a token right after a line break, a tab or a `\u`
   escape (#281), Google API keys (#282), a token after an ANSI escape
   (#284) and several other shapes (#285).
5. Record who reviewed which files and when (UTC); the write-up states it.

## 12. Human actions

Keep this list while you work, in `$EV/human-actions.md`; the write-up
publishes it (Requirement 5). Everything not in it was done by AutoForge or
by the agents it launched.

| # | Time (UTC) | Who | Action | Command or UI | Why | Artifact or trace reference |
|---|---|---|---|---|---|---|
| 1 | | maintainer | Created and pushed the repository; tagged `demo-start` | `gh repo create ...` | the demo repository | repository, `demo-start` |
| 2 | | maintainer | Set workflow permissions, the ruleset and interaction limits | `gh api ...` (section 5) | containment | `ruleset.json`, `interaction-limits-set.json` |
| 3 | | maintainer | Filed the EPIC and the issue | `gh issue create ...` | the run's input | EPIC #, issue # |
| 4 | | maintainer | Created the fine-grained token; logged in to the providers; set spend limits | settings UI, `claude auth login`, `opencode auth login` | credentials | `spend-plan.md` |
| 5 | | maintainer | Ran `doctor` and the dry run | `autoforge --config autoforge.demo.yaml --state-dir .autoforge/issue-<n> doctor` / `run ... --dry-run` | preflight | `doctor.json`, `dry-run.txt` |
| 6 | | maintainer | Authorized the paid calls | `spend-plan.md` | decision on #261 | |
| 7 | | maintainer | Started the run | `autoforge --config autoforge.demo.yaml --state-dir .autoforge/issue-<n> run --epic <url> --issue <url>` | | run id |
| | | maintainer | (each `resume`, `unblock`, approval, comment) | the exact command | the reason given | step or comment |
| | | maintainer | Lifted the interaction limit | `gh api -X DELETE ...` | run over | |
| | | maintainer | Merged the PR (if) | `gh pr merge ...` | human merge | merge commit |
| | | maintainer | Revoked the token | settings UI | | |

## 13. The write-up

Fill in [`docs/demo-writeup-template.md`](demo-writeup-template.md) from the
published excerpts only, publish it where #261 says (a `docs/demo.md` in
AutoForge or this repository's README), and post a comment on #261 linking
the repository, the issue, the PR and the write-up and naming the AutoForge
commit. At the release candidate, re-run the demo on the RC or record on
#255 why no change since the demo commit affects it (Gate 3).

## 14. Reproducing the demo on your fork

Expect different code, findings and timings; the phase sequence is what
reproduces. Nothing reaches the upstream repository: AutoForge opens the PR
in the issue's own repository.

1. Fork and clone, default branch only, so no `autoforge/*` branch of the
   original run comes along:

   ```bash
   gh repo fork iceboundrock/autoforge-demo --clone --default-branch-only
   cd autoforge-demo
   git fetch upstream refs/tags/demo-start:refs/tags/demo-start
   git push origin demo-start
   gh repo set-default <you>/autoforge-demo
   ```

   `gh repo fork --clone` makes your fork `origin` and the original
   `upstream`, and sets `upstream` as `gh`'s default repository;
   `set-default` points `gh` at your fork. AutoForge itself takes the
   repository from `origin`. The tag is pushed to your fork so that the
   checks of section 7 find it there.

2. If the original PR was merged (`git rev-parse HEAD` differs from
   `git rev-parse 'demo-start^{commit}'`), base your run on the state before
   it, as a branch that becomes your fork's default:

   ```bash
   git push origin 'demo-start^{commit}:refs/heads/demo-base'
   gh repo edit <you>/autoforge-demo --default-branch demo-base
   git fetch origin && git checkout -B demo-base origin/demo-base
   ```

   CI's `push` trigger names `main` only, so a `demo-base` default branch
   gets checks on pull requests but no `push` run; with the merge gate
   closed AutoForge does not need one.
3. Enable issues (`gh repo edit <you>/autoforge-demo --enable-issues`) and,
   in the fork's Actions tab, enable workflows.
4. Apply the ruleset (section 5, with your repository), and preferably the
   interaction limit.
5. Use your own dedicated user, your own fine-grained token scoped to your
   fork with the permissions of section 4, and your own provider logins and
   spend limits (sections 1, 4, 6).
6. File the EPIC and the issue from `issues/` as in section 5 with your
   repository, install AutoForge at the commit the write-up names (section 3),
   and follow sections 7 and 8 with your repository's URLs.

The run should pass through `INITIALIZING`, `ANALYZE_EXECUTE`, `REVIEW` (and
`FIX` and `REVIEW` again when the review finds something) and stop at
`READY_FOR_MERGE` on a PR in your fork.
