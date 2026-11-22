import json
import os
import re
import urllib.request


URL = "https://exam.sanand.workers.dev/exam-tds-2026-09-ga5.js"
BASELINE = "questions.json"


def main():
    request = urllib.request.Request(URL, headers={"User-Agent": "tds-question-monitor"})
    with urllib.request.urlopen(request, timeout=30) as response:
        source = response.read().decode("utf-8")

    # Question bundles declare stable IDs and titles in their question constructors.
    found = re.findall(r'let\s+\w+\s*=\s*"(q-[a-z0-9-]+)"\s*,\s*\w+\s*=\s*"([^"]+)"', source)
    if not found:
        raise RuntimeError("Could not find question IDs and titles in the downloaded bundle")
    current = dict(found)

    if os.path.exists(BASELINE):
        with open(BASELINE, encoding="utf-8") as file:
            previous = json.load(file)
    else:
        previous = current

    added = {key: value for key, value in current.items() if key not in previous}
    removed = {key: value for key, value in previous.items() if key not in current}
    changed = bool(added or removed)

    with open(BASELINE, "w", encoding="utf-8") as file:
        json.dump(current, file, indent=2, ensure_ascii=False)
        file.write("\n")

    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as file:
        file.write(f"changed={str(changed).lower()}\n")
        file.write("title=TDS 2026 Sep GA5\n")
        file.write(f"added={json.dumps(list(added.values()))}\n")
        file.write(f"removed={json.dumps(list(removed.values()))}\n")


if __name__ == "__main__":
    main()
