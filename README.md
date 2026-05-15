# Roadmap Disk CSD-PIBT Prototype

This repo contains notes and a minimal Python proof harness for a restricted
Continuous-Space Dependency PIBT idea: disk agents moving on a clearance-valid
2D roadmap with finite candidate reservations.

Run the prototype tests with:

```bash
uv run pytest -q
```

The implementation lives in `csd_pibt/`. The first formal model note is
`knowledge/08-roadmap-disk-spec.md`.
