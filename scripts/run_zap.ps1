docker run --rm -v "${PWD}:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable `
  zap-baseline.py -t http://host.docker.internal:8000 `
  -c .zap/rules.tsv -r zap-report.html -J zap-report.json -a -j
