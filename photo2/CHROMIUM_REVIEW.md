# Persistent local Chromium review launcher

Installed on daisy for rharris, 2026-10-14, by explicit user request (R283).

Run the executable directly, using its absolute path, with exactly one module:

```bash
/home/rharris/.local/bin/beads-chromium-review photo2.r282.browser_check
```

Future rounds use the same launcher with their existing `photo2.rNNN.browser_check`
module (three or more ASCII digits). Do not wrap this invocation in Bash, prefix it
with environment assignments, or request a general Python/Bash permission. When a
Codex tool needs an outside-sandbox execution request, use this same executable as
the command; its persistent rule handles permission in sessions that load the rule.

## Installed configuration

- Executable: `/home/rharris/.local/bin/beads-chromium-review` (0755), copied from
  [the tracked source](tools/beads-chromium-review), not symlinked to the checkout.
- Fixed checkout: `/home/rharris/git/beads`; fixed interpreter: `.venv/bin/python`.
- Browser cache: `/home/rharris/.cache/beads-playwright`, copied from the existing
  `/tmp/beads-debugger-browsers` installation so it survives reboot/tmp cleanup.
- Rule file: `/home/rharris/.codex/rules/default.rules`; all pre-existing bytes preserved.
- Original backup: `default.rules.before-beads-chromium-review.bak` in that directory.

The appended rule has this exact prefix and decision, plus explanation and inline
positive/negative matching examples:

```python
prefix_rule(
    pattern = ["/home/rharris/.local/bin/beads-chromium-review"],
    decision = "allow",
)
```

The prefix rule covers the executable; the executable itself validates arguments.
It accepts only one existing non-symlink module file under the fixed `photo2/rNNN`
path. It rejects other module names, paths, interpreter options, shell text and extra
arguments. Both launcher and child use isolated Python startup. The child receives
a small environment with fixed browser/cache paths; caller PYTHONPATH, Node options,
round output overrides and alternative browser paths are not forwarded. No shell
command is constructed from module input. The bootstrap is fixed code, not caller code.

## Verification

```bash
codex execpolicy check --pretty \
  --rules /home/rharris/.codex/rules/default.rules \
  -- /home/rharris/.local/bin/beads-chromium-review photo2.r282.browser_check
.venv/bin/python -m unittest photo2.tools.test_chromium_launcher
```

Codex CLI0.162.1 reported `decision: allow`. Four policy checks show that the launcher
is allowed while unrestricted Python, project Python and Bash commands do not match
an allow rule. Five contract tests and five direct rejection checks pass. The installed
launcher ran R282's22 browser panels successfully, with no changed scientific artifacts.
[Recorded validation](tools/chromium-review-validation.json).

## Restart and limits

**Restart the active Codex CLI/app process once to reliably load this manually edited
rule.** The official [rules documentation](https://learn.chatgpt.com/docs/agent-configuration/rules)
says rules are scanned at startup. The explicit `execpolicy check` reads the file
immediately; today's outside-sandbox run proves the launcher works, not that every
already-running client automatically reloads it. Future Codex sessions using this
same user config load the rule. No machine reboot or new project conversation is needed.

This is a local user configuration, not a portable permission shipped by Git. Other
machines, accounts, relocated checkouts or different CODEX_HOME settings require
corresponding installation/configuration. More restrictive managed policies can still
require approval or forbid execution; local `.rules` support must not be assumed for
Work Cloud/local-executor environments. Use the absolute command path for an exact match.

The launcher trusts the project's browser checks, their imports, the virtual environment
and installed browser binaries. Its argument restriction is not a sandbox around that
trusted code. Future modules matching the requested naming convention are eligible
without a new prefix rule; review their code normally. It does not install dependencies,
download browsers, or accept browser-install commands. A Playwright upgrade may require
a matching Chromium build in the persistent cache. Existing unrelated permission rules
were preserved rather than audited or broadened. Only the launcher permission was added.
