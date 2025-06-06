# Ollama Distribution Packager

This repository contains the necessary files to create a distributable offline installation package for Ollama.

## How to Build the Package

A helper script `package.sh` is provided to automate the creation of the distribution tarball.

To build the package, simply run this script from the project's root directory:
```bash
bash package.sh
```

The script will perform the following actions:
1.  Download the latest ARM64 version of the Ollama binary (`ollama-linux-arm64.tgz`).
2.  Place the downloaded binary inside the `ollama_dist` directory.
3.  Create a new tarball (e.g., `ollama_dist_arm64_YYYYMMDD.tar.gz`) in the root directory.

The resulting tarball is the complete, self-contained package ready for distribution to end-users. 