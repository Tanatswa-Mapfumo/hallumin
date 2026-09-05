# MScProject Software Submission

This archive contains the executable and source submission for Tanatswa
Mapfumo's MSc project on evidence-grounded table-to-text generation.

## Start here

1. Read `PROGRAM_DESCRIPTION.pdf` for the one-page program overview.
2. Follow `INSTALLATION_AND_BUILD.md` to install the wheel or source package.
3. Review `DEPENDENCIES.md` for supported and verified versions.
4. Review `VERIFICATION.md` for the completed acceptance checks.
5. Run `examples/run_deterministic_demo.sh` for an API-free smoke test.

## Archive layout

| Path | Contents |
| --- | --- |
| `executable/` | Platform-independent Python wheel with both console commands |
| `source/MScProject/` | Maintained source, tests, notebooks, configuration, documentation, and curated evaluation evidence |
| `examples/` | Small sample input and deterministic demonstration |
| `documentation/` | Full readable program-listings PDF |
| `SOFTWARE_MANIFEST.json` | File sizes and SHA-256 digests |
| `CHECKSUMS.sha256` | Standard checksum list for archived payload files |

## Principal commands

```bash
table2text --help
table2text-evaluate --help
```

No secret keys, completed `.env` files, downloaded model weights, local virtual
environments, caches, or transient development runs are included.
