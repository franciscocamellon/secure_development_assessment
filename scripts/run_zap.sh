#!/usr/bin/env bash
set +e
docker run --rm --network host -v "$PWD:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://127.0.0.1:8000 \
  -c .zap/rules.tsv -r zap-report.html -J zap-report.json -a -j
code=$?
set -e
if [ "$code" -eq 1 ]; then exit 1; fi
if [ "$code" -ne 0 ] && [ "$code" -ne 2 ]; then exit "$code"; fi
exit 0
