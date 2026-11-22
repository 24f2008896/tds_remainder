import json
import os
import re
import urllib.request


CONFIG = "assignment.json"


def main():
    with open(CONFIG, encoding="utf-8") as file:
        config = json.load(file)

    request = urllib.request.Request(
        config["bundle_url"], headers={"User-Agent": "tds-question-monitor"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        source = response.read().decode("utf-8")

    # Question bundles declare stable IDs and titles in their question constructors.
    found = re.findall(r'let\s+\w+\s*=\s*"(q-[a-z0-9-]+)"\s*,\s*\w+\s*=\s*"([^"]+)"', source)
    if not found:
        raise RuntimeError("Could not find question IDs and titles in the downloaded bundle")
    current = dict(found)

    baseline_path = config["baseline_file"]
    if os.path.exists(baseline_path):
        with open(baseline_path, encoding="utf-8") as file:
            previous = json.load(file)
    else:
        previous = current

    added = {key: value for key, value in current.items() if key not in previous}
    removed = {key: value for key, value in previous.items() if key not in current}
    changed = bool(added or removed)

    with open(baseline_path, "w", encoding="utf-8") as file:
        json.dump(current, file, indent=2, ensure_ascii=False)
        file.write("\n")

    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as file:
        file.write(f"changed={str(changed).lower()}\n")
        file.write(f"title={config['title']}\n")
        file.write(f"baseline_file={baseline_path}\n")
        file.write(f"page_url={config['page_url']}\n")
        file.write(f"added={json.dumps(list(added.values()))}\n")
        file.write(f"removed={json.dumps(list(removed.values()))}\n")

    print(f"Assignment: {config['title']}")
    print(f"Question count: {len(current)}")
    print(f"Question list changed: {changed}")
    if added:
        print(f"Added: {list(added.values())}")
    if removed:
        print(f"Removed: {list(removed.values())}")


if __name__ == "__main__":
    main()
