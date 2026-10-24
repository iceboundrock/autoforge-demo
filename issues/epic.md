This EPIC exists so that [AutoForge](https://github.com/iceboundrock/AutoForge) can be demonstrated end to end on this repository ([iceboundrock/AutoForge#261](https://github.com/iceboundrock/AutoForge/issues/261)). `autoforge run` takes an EPIC as well as the issue it works on; this is that EPIC.

## Scope

Small, self-contained features of the `wordstat` command, one issue each. An AutoForge run implements each issue, has it reviewed independently and, when the review finds something, fixed and reviewed again. The run stops when the pull request is ready for a human to merge.

## Issues

The issues are listed as sub-issues of this EPIC.

## How this EPIC is maintained

- The maintainer files the issues and starts each run.
- AutoForge's merge gate is closed for the demo (`safety.allow_merge: false` in `autoforge.demo.yaml`). AutoForge therefore never merges, and never edits this EPIC: its EPIC update follows a merge, so it is never reached. The maintainer updates this EPIC by hand.
- The configuration and the operator runbook are in the repository: `autoforge.demo.yaml` and `docs/RUNBOOK.md`.
