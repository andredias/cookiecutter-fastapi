#!/bin/bash

if [ "{{cookiecutter.version_control}}" == "hg" ]; then
    hg init .
    echo '[hooks]
precommit.lint = (cd `hg root`; poetry run make lint)
pre-push.test = (cd `hg root`; poetry run make test)
' >> .hg/hgrc
else
    git init .
    echo '#!/bin/bash

cd $(git rev-parse --show-toplevel)
poetry run make lint
' > .git/hooks/pre-commit
    echo '#!/bin/bash

cd $(git rev-parse --show-toplevel)
poetry run make test
' > .git/hooks/pre-push
    chmod +x .git/hooks/pre-{commit,push}
fi

poetry install
