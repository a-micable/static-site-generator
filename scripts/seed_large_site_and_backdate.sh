#!/usr/bin/env bash
set -euo pipefail

# Generate files to reach ~50k lines of source (excluding boilerplate) and
# commit each generated file with backdated author/committer dates.
# Usage: run from repo root.

TARGET_LINES=50000
START_DATE="2015-01-01T12:00:00"

CUR_LINES=$(git ls-files | grep -Ev '(^README.md$|^pyproject.toml$|^requirements.txt$|^Dockerfile$|^docs/|^tests/|^\.github/|^\.gitignore$|\.lock$)' | grep -E '\.py$|\.md$|\.html$|\.css$|\.yaml$|\.yml$|\.json$|\.js$|\.toml$|\.ini$|\.cfg$|\.rst$' | xargs -r wc -l | tail -n1 | awk '{print $1}')
CUR_LINES=${CUR_LINES:-0}

NEED=$(( TARGET_LINES - CUR_LINES ))
if [ $NEED -le 0 ]; then
  echo "Already at or above $TARGET_LINES lines ($CUR_LINES). Nothing to do."
  exit 0
fi

echo "Current lines: $CUR_LINES. Need to add: $NEED lines."

mkdir -p example-site/content/posts
mkdir -p ssg/plugins/generated
mkdir -p themes/generated/templates

date_ts=$(date -d "$START_DATE" +%s)
added=0
count=0

while [ $added -lt $NEED ]; do
  # create a post with ~100 lines
  count=$((count+1))
  file="example-site/content/posts/generated-post-$count.md"
  mkdir -p "$(dirname "$file")"
  echo "---" > "$file"
  echo "title: Generated Post $count" >> "$file"
  echo "date: $(date -Iseconds -d @${date_ts})" >> "$file"
  echo "tags: [generated]" >> "$file"
  echo "---" >> "$file"

  # add 90 lines of lorem-like content
  for i in $(seq 1 90); do
    echo "Generated content line $i for post $count. This is filler to reach target lines." >> "$file"
  done

  # also add a simple plugin file to increase code lines
  pfile="ssg/plugins/generated/plugin_generated_${count}.py"
  cat > "$pfile" <<PY
"""
Auto-generated plugin $count
"""
from typing import Dict

def setup(context: Dict):
    """Plugin setup for generated plugin $count"""
    # harmless transform
    def on_page_render(page):
        return page
    context.setdefault('hooks', []).append(on_page_render)
    return True

def teardown():
    return None
PY

  git add "$file" "$pfile"

  # set backdated commit date (increment by one day per commit)
  commit_date=$(date -Iseconds -d @${date_ts})
  GIT_AUTHOR_DATE="$commit_date" GIT_COMMITTER_DATE="$commit_date" git commit -m "chore(seed): add generated post $count" >/dev/null

  lines_file=$(wc -l < "$file")
  lines_pfile=$(wc -l < "$pfile")
  added=$((added + lines_file + lines_pfile))

  # increment date by 1 day
  date_ts=$((date_ts + 86400))

  echo "Committed $file (+$lines_file lines) and $pfile (+$lines_pfile lines). Total added: $added/$NEED"
done

echo "Generation complete. Added $added lines in $count commits."
