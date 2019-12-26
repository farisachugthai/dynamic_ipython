#!/bin/bash
# Maintainer: Faris Chugthai

# set -euo pipefail

git tag -d 6.0.0 6.0.0rc1 6.1.0 6.2.0 6.3.0 7.0.0 7.0.0-doc 7.0.0b1 7.0.0rc1 7.0.1 rel-0.11 rel-0.12 rel-0.13 rel0.8.4 rel-1.0.0 rel-2.0.0 rel-3.0.0 rel-4.0.0 rel-4.0.0b1
git tag --delete 1.0.0a1 3.0.0-dev 4.0.0 5.0.0 5.0.0b1  5.0.0b2 5.0.0b3 5.0.0b4 5.0.0rc1
git tag -d list rel-0.8.4 rel-4.1.0rc2 5.1.0 7.1.0 7.1.1 7.10.0 7.10.1 7.2.0 7.3.0 7.4.0 7.5.0 7.6.0 7.6.1 7.7.0 7.8.0 7.9.0
