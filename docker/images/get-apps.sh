#!/usr/bin/env bash
set -euo pipefail

APPS_JSON_PATH="/tmp/apps.json"
echo "Decoding APPS_JSON_BASE64..."
if [ -z "${APPS_JSON_BASE64:-}" ]; then
  echo "APPS_JSON_BASE64 is empty — nothing to clone."
  exit 0
fi

# Decode to file
echo "${APPS_JSON_BASE64}" | base64 -d > "${APPS_JSON_PATH}"

# Validate JSON array
if ! jq -e . "${APPS_JSON_PATH}" >/dev/null 2>&1 ; then
  echo "apps.json is invalid JSON"
  cat "${APPS_JSON_PATH}"
  exit 1
fi

echo "navigating into bench folder : ${BENCH_PATH}"
cd "${BENCH_PATH}"

# For each app entry { "url": "...", "branch": "..." }
jq -c '.[]' "${APPS_JSON_PATH}" | while read -r entry; do
  url=$(echo "$entry" | jq -r '.url // empty')
  branch=$(echo "$entry" | jq -r '.branch // empty')
  if [ -z "$url" ] || [ "$url" = "null" ]; then
    echo "Skipping entry without url: $entry"
    continue
  fi

  echo "Running bench get-app $url (branch: ${branch:-default})"
  # Use shallow clone for speed
  if [ -n "$branch" ] && [ "$branch" != "null" ]; then
    bench get-app --branch "$branch" "$url"
  else
    bench get-app "$url"
  fi

  # If the app has a requirements.txt or setup.py and you want to install deps now:
  # (Uncomment the pip install lines if desired and safe in your environment)
  # if [ -f "$dest/requirements.txt" ]; then
  #   echo "Installing python requirements for $name"
  #   python3 -m pip install --user -r "$dest/requirements.txt"
  # fi
  # if [ -f "$dest/setup.py" ] || [ -f "$dest/pyproject.toml" ]; then
  #   echo "Installing editable package for $name"
  #   python3 -m pip install --user -e "$dest"
  # fi
done

# ensure correct permissions
chown -R frappe:frappe "${APPS_DIR}"
echo "Done cloning apps."