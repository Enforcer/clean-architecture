#!/usr/bin/env bash

NORMALIZED_NAME=$(echo "$@" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
NORMALIZED_NAME=${NORMALIZED_NAME:?please provide the name of new microlib}

echo "Creating $NORMALIZED_NAME"
mkdir -p "$NORMALIZED_NAME"
STRUCTURE=(
    "$NORMALIZED_NAME/$NORMALIZED_NAME"
    "$NORMALIZED_NAME/$NORMALIZED_NAME/application"
    "$NORMALIZED_NAME/$NORMALIZED_NAME/application/queries"
    "$NORMALIZED_NAME/$NORMALIZED_NAME/application/repositories"
    "$NORMALIZED_NAME/$NORMALIZED_NAME/application/use_cases"
    "$NORMALIZED_NAME/$NORMALIZED_NAME/domain"
    "$NORMALIZED_NAME/$NORMALIZED_NAME/domain/entities"
    "$NORMALIZED_NAME/tests"
    "$NORMALIZED_NAME/tests/application"
    "$NORMALIZED_NAME/tests/domain"
)
for dirname in "${STRUCTURE[@]}"; do
    mkdir -p "$dirname"
    touch "$dirname/__init__.py"
done

INFRASTRUCTURE_NAME="${NORMALIZED_NAME}_infrastructure"

echo "Creating $INFRASTRUCTURE_NAME"
mkdir -p "$INFRASTRUCTURE_NAME"
STRUCTURE=(
    "$INFRASTRUCTURE_NAME/$INFRASTRUCTURE_NAME"
    "$INFRASTRUCTURE_NAME/$INFRASTRUCTURE_NAME/queries"
    "$INFRASTRUCTURE_NAME/$INFRASTRUCTURE_NAME/repositories"
    "$INFRASTRUCTURE_NAME/tests"
    "$INFRASTRUCTURE_NAME/tests/repositories"
)
for dirname in "${STRUCTURE[@]}"; do
    mkdir -p "$dirname"
    touch "$dirname/__init__.py"
done

for dirname in "$NORMALIZED_NAME" "$INFRASTRUCTURE_NAME"; do
echo "[isort]
known_current=$dirname" > "$dirname/.isort.cfg"
echo "[pytest]" > "$dirname/pytest.ini"
touch "$dirname/requirements.txt"
touch "$dirname/requirements-dev.txt"
echo "from setuptools import find_packages, setup

setup(
    name=\"$dirname\",
    version=\"0.0.0\",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
)
" > "$dirname/setup.py"
done
