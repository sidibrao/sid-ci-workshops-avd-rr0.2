# ANTA Validation Summary

This file is the committed, repo-level summary of the ANTA validation for the full L3LS EVPN home lab.

The detailed ANTA reports are generated locally by AVD and are intentionally ignored by Git because they are runtime artifacts:

| Site | Local Markdown Report | Local JSON Report | Local CSV Report |
| --- | --- | --- | --- |
| Site 1 | `sites/site_1/anta/reports/anta_report.md` | `sites/site_1/anta/reports/anta_report.json` | `sites/site_1/anta/reports/anta_report.csv` |
| Site 2 | `sites/site_2/anta/reports/anta_report.md` | `sites/site_2/anta/reports/anta_report.json` | `sites/site_2/anta/reports/anta_report.csv` |

## Latest Run

| Field | Value |
| --- | --- |
| Date | 2026-05-28 |
| Scope | Site 1 and Site 2 fabrics |
| Tool | AVD `arista.avd.anta_runner` |
| Site 1 command | `make validate-site-1` |
| Site 2 command | `make validate-site-2` |

## Result Summary

| Site | Total Tests | Success | Skipped | Failure | Error | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Site 1 | 48 | 0 | 36 | 12 | 0 | Live ANTA run completed; failures are listed below. |
| Site 2 | 45 | 0 | 36 | 9 | 0 | Live ANTA run completed; failures are listed below. |

## Current Findings

| Area | Site 1 | Site 2 | Meaning |
| --- | --- | --- | --- |
| NTP | 6 failures | 6 failures | NTP is disabled or unsynchronised in the lab images. |
| LLDP neighbor naming | 3 failures | 3 failures | AVD expected short hostnames, while EOS reports neighbors with the `dns.google` domain suffix. |
| Logging errors | 3 failures | 0 failures | Historical BGP/BFD syslog messages are still present in the device logs. |
| vEOS hardware checks | 30 skipped | 30 skipped | Expected for vEOS-lab; fan, PSU, temperature, transceiver, and storm-control checks are unsupported. |

## Interpretation

The ANTA workflow is working and producing real reports for both sites.

The current failures are not showing a broken EVPN/MLAG/WAN data-plane by themselves. They are validation hygiene items:

- Enable or tune NTP if you want `VerifyNTP` to pass.
- Align LLDP hostname expectations with the FQDN format reported by EOS, or adjust the lab DNS domain behavior.
- Clear old logs or tune the logging validation if historical BGP/BFD events should not fail the report.
- Keep vEOS hardware checks skipped, or customize the catalog to remove unsupported hardware tests for this lab.

## How To Regenerate

From `labs/L3LS_EVPN`:

```bash
export ANSIBLE_USER="admin"
export ANSIBLE_PASSWORD="<your-lab-password>"

make validate-site-1
make validate-site-2
```

To generate catalogs without touching devices:

```bash
make anta-dry-run-all
```

## Optional Word Document

This Markdown file can be opened directly in VS Code or GitHub. If you want a Word document, convert it locally with Pandoc:

```bash
pandoc docs/anta-validation-summary.md -o docs/anta-validation-summary.docx
```
