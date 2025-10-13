#!/usr/bin/env bash
set -euo pipefail

TARGET_BRANCH="${1:-master}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found in PATH." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "This script must be run inside a git repository." >&2
  exit 1
fi

cd "${REPO_ROOT}"

current_branch="$(git branch --show-current)"
if [[ "${current_branch}" != "${TARGET_BRANCH}" ]]; then
  echo "Current branch '${current_branch}' does not match target branch '${TARGET_BRANCH}'." >&2
  echo "Pass the desired branch as an argument, e.g. './tools/git-auto-commit-push.sh feature-branch'." >&2
  exit 1
fi

if ! git diff --cached --quiet; then
  echo "Staged changes detected. Please commit or reset them before running this workflow." >&2
  exit 1
fi

if git status --porcelain | grep -qE '^(AA|DD|U.|.U)'; then
  echo "Unmerged files detected. Resolve merge conflicts before running this workflow." >&2
  exit 1
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "No changes detected. Nothing to commit." >&2
  exit 0
fi

categories=(frontend backend docs config other)

declare -a frontend_display=()
declare -a frontend_stage=()
declare -a backend_display=()
declare -a backend_stage=()
declare -a docs_display=()
declare -a docs_stage=()
declare -a config_display=()
declare -a config_stage=()
declare -a other_display=()
declare -a other_stage=()

declare -A has_new=()
declare -A has_delete=()
declare -A has_rename=()
for cat in "${categories[@]}"; do
  has_new["${cat}"]=false
  has_delete["${cat}"]=false
  has_rename["${cat}"]=false
done

trim() {
  local text="$1"
  text="${text#${text%%[![:space:]]*}}"
  text="${text%${text##*[![:space:]]}}"
  printf '%s' "${text}"
}

categorize_path() {
  local path="$1"
  case "${path}" in
    docs/*|*.md|*.MD|*.markdown|*.rst)
      echo "docs"
      ;;
    frontend/*)
      echo "frontend"
      ;;
    backend/*)
      echo "backend"
      ;;
    render.yaml|render.yml|Dockerfile|docker-compose.*|*.env|*.env.*|*.ini|*.toml|*.lock|requirements*.txt|runtime.txt|pnpm-lock.yaml|package-lock.json|package.json|tsconfig.json|eslint.config.*|prettier.config.*|*.config|*.cfg|*.conf)
      echo "config"
      ;;
    *)
      echo "other"
      ;;
  esac
}

add_display_path() {
  local category="$1"
  local path="$2"
  local var_name="${category}_display"
  local -n arr="${var_name}"
  for existing in "${arr[@]}"; do
    if [[ "${existing}" == "${path}" ]]; then
      return
    fi
  done
  arr+=("${path}")
}

add_stage_path() {
  local category="$1"
  local path="$2"
  local var_name="${category}_stage"
  local -n arr="${var_name}"
  for existing in "${arr[@]}"; do
    if [[ "${existing}" == "${path}" ]]; then
      return
    fi
  done
  arr+=("${path}")
}

build_focus_text() {
  local category="$1"
  local var_name="$2"
  local -n display_paths="${var_name}"
  declare -A seen=()
  local -a focus_list=()

  for path in "${display_paths[@]}"; do
    local trimmed="${path}"
    case "${category}" in
      frontend)
        trimmed="${trimmed#frontend/}"
        ;;
      backend)
        trimmed="${trimmed#backend/}"
        ;;
      docs)
        trimmed="${trimmed#docs/}"
        ;;
    esac
    trimmed="${trimmed#/}"
    [[ -z "${trimmed}" ]] && trimmed="${category}"

    local focus=""
    case "${category}" in
      frontend|backend)
        IFS='/' read -r first second _ <<< "${trimmed}"
        focus="${first}"
        if [[ -n "${second}" ]]; then
          focus+="/${second}"
        fi
        ;;
      docs|config|other)
        focus="$(basename "${trimmed}")"
        ;;
    esac
    focus="${focus:-${category}}"

    if [[ -z "${seen["${focus}"]+x}" ]]; then
      seen["${focus}"]=1
      focus_list+=("${focus}")
    fi
  done

  local count="${#focus_list[@]}"
  if (( count == 0 )); then
    printf ''
  elif (( count == 1 )); then
    printf '%s' "${focus_list[0]}"
  elif (( count == 2 )); then
    printf '%s and %s' "${focus_list[0]}" "${focus_list[1]}"
  else
    printf '%s, %s and %d others' "${focus_list[0]}" "${focus_list[1]}" "$((count - 2))"
  fi
}

create_summary() {
  local category="$1"
  local focus
  focus="$(build_focus_text "${category}" "${category}_display")"
  focus="$(trim "${focus}")"

  case "${category}" in
    frontend)
      if [[ -n "${focus}" ]]; then
        printf 'update %s' "${focus}"
      else
        printf 'update frontend modules'
      fi
      ;;
    backend)
      if [[ -n "${focus}" ]]; then
        printf 'update %s' "${focus}"
      else
        printf 'update backend services'
      fi
      ;;
    docs)
      if [[ -n "${focus}" ]]; then
        printf 'refresh %s' "${focus}"
      else
        printf 'refresh documentation'
      fi
      ;;
    config)
      if [[ -n "${focus}" ]]; then
        printf 'adjust %s' "${focus}"
      else
        printf 'adjust configuration'
      fi
      ;;
    other)
      if [[ -n "${focus}" ]]; then
        printf 'update %s' "${focus}"
      else
        printf 'synchronize miscellaneous changes'
      fi
      ;;
  esac
}

determine_prefix() {
  local category="$1"
  local new_flag="${has_new["${category}"]}"
  local delete_flag="${has_delete["${category}"]}"
  local rename_flag="${has_rename["${category}"]}"

  case "${category}" in
    docs)
      echo "docs"
      ;;
    config)
      echo "chore"
      ;;
    frontend|backend)
      if [[ "${rename_flag}" == "true" ]]; then
        echo "refactor"
      elif [[ "${new_flag}" == "true" && "${delete_flag}" != "true" ]]; then
        echo "feat"
      elif [[ "${delete_flag}" == "true" && "${new_flag}" != "true" ]]; then
        echo "refactor"
      else
        echo "chore"
      fi
      ;;
    other)
      if [[ "${new_flag}" == "true" && "${delete_flag}" != "true" ]]; then
        echo "feat"
      else
        echo "chore"
      fi
      ;;
  esac
}

build_commit_message() {
  local category="$1"
  local prefix
  prefix="$(determine_prefix "${category}")"
  local summary
  summary="$(create_summary "${category}")"
  summary="$(trim "${summary}")"

  if [[ -z "${summary}" ]]; then
    summary="update ${category} files"
  fi

  if [[ "${category}" == "docs" ]]; then
    printf '%s: %s' "${prefix}" "${summary}"
  else
    printf '%s(%s): %s' "${prefix}" "${category}" "${summary}"
  fi
}

record_status_flags() {
  local category="$1"
  local status="$2"

  if [[ "${status}" == "??" || "${status:0:1}" == "A" || "${status:1:1}" == "A" || "${status:0:1}" == "C" || "${status:1:1}" == "C" ]]; then
    has_new["${category}"]="true"
  fi
  if [[ "${status:0:1}" == "D" || "${status:1:1}" == "D" ]]; then
    has_delete["${category}"]="true"
  fi
  if [[ "${status:0:1}" == "R" || "${status:1:1}" == "R" ]]; then
    has_rename["${category}"]="true"
  fi
}

while IFS= read -r -d '' entry; do
  status="${entry:0:2}"
  path="${entry:3}"
  old_path=""

  if [[ "${status:0:1}" == "R" || "${status:0:1}" == "C" ]]; then
    old_path="${path}"
    IFS= read -r -d '' new_path || true
    path="${new_path}"
  fi

  category="$(categorize_path "${path}")"
  add_display_path "${category}" "${path}"
  add_stage_path "${category}" "${path}"
  record_status_flags "${category}" "${status}"

  if [[ -n "${old_path}" ]]; then
    add_stage_path "${category}" "${old_path}"
    has_rename["${category}"]="true"
  fi

done < <(git status --porcelain=v1 -z)

commits_created=0

for category in "${categories[@]}"; do
  stage_var="${category}_stage"
  declare -n stage_paths="${stage_var}"
  if (( "${#stage_paths[@]}" == 0 )); then
    continue
  fi

  echo "Preparing ${category} changes (${#stage_paths[@]} paths)"
  git add -- "${stage_paths[@]}"

  commit_message="$(build_commit_message "${category}")"
  echo "Committing with message: ${commit_message}"
  git commit -m "${commit_message}"
  ((commits_created+=1))

done

if (( commits_created == 0 )); then
  echo "No commits were created. Review pending changes manually." >&2
  exit 1
fi

git fetch origin "${TARGET_BRANCH}" >/dev/null 2>&1 || true

if git rev-parse --verify "origin/${TARGET_BRANCH}" >/dev/null 2>&1; then
  read -r behind ahead < <(git rev-list --left-right --count "origin/${TARGET_BRANCH}...HEAD")
  if (( behind > 0 )); then
    echo "Local branch is behind origin/${TARGET_BRANCH} by ${behind} commit(s). Run 'git pull --rebase origin ${TARGET_BRANCH}' and resolve before pushing." >&2
    exit 1
  fi
else
  echo "Remote branch origin/${TARGET_BRANCH} was not found. The push step will create it." >&2
fi

echo "Pushing commits to origin/${TARGET_BRANCH}"
if git push origin "${TARGET_BRANCH}"; then
  echo "Push successful."
else
  echo "Push failed. Inspect the output above for details." >&2
  exit 1
fi

remaining_status="$(git status --short)"
if [[ -n "${remaining_status}" ]]; then
  echo "Warning: the working tree still has pending changes:" >&2
  echo "${remaining_status}" >&2
else
  echo "Working tree is clean."
fi

printf '\nWorkflow complete.\n'
