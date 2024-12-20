#!/usr/bin/env bash


GIT_PRE_PUSH='#!/usr/bin/env bash
cd $(git rev-parse --show-toplevel)
make lint && make test
'

echo "$GIT_PRE_PUSH" > .git/hooks/pre-push
chmod +x .git/hooks/pre-*
