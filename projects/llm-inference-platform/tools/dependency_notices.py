# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Record installed dependency versions and preserve their packaged notices."""
from importlib.metadata import distribution
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def generate():
    runtime = {line.split('==')[0] for line in (ROOT / 'requirements.txt').read_text().splitlines()}
    rows = []
    for line in (ROOT / 'requirements-dev.txt').read_text().splitlines():
        name, expected = line.split('==')
        package = distribution(name)
        if package.version != expected:
            raise ValueError(f'{name}: installed version does not match the pinned version')
        license_name = package.metadata.get('License-Expression') or package.metadata.get('License')
        if not license_name or '\n' in license_name:
            license_name = 'See packaged notices'
        notices = [file for file in package.files or []
                   if '.dist-info/' in str(file) and any(
                       part in str(file).lower() for part in ('license', 'copying', 'notice'))]
        if not notices:
            raise ValueError(f'{name}: no packaged license files found; manual review required')
        links = []
        for file in notices:
            # Preserve directory structure to avoid colliding notice filenames.
            relative = str(file).split('.dist-info/', 1)[1]
            destination = ROOT / 'third_party' / name / expected / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(package.locate_file(file), destination)
            links.append(f'[{file.name}]({destination.relative_to(ROOT).as_posix()})')
        role = 'Runtime' if name in runtime else 'Development'
        rows.append(f'| {name} | {expected} | {role} | {license_name} | {", ".join(links)} |')
    preamble = '''# Third-party dependency notices

These Python packages retain their own copyrights and licenses. The project's
Apache 2.0 license does not replace or restrict the rights granted by their licenses.
The table records package metadata, not a legal compatibility determination.
Full notices below are copied unchanged from the installed distributions.

Regenerate after dependency changes with `python tools/dependency_notices.py`
in the pinned development environment. Review removed-version directories before
release; this script does not delete old notices automatically. Review additional
native components, model assets, and container contents separately before bundling
them. No model weights or datasets are distributed by this project.

| Package | Version | Use | Declared license | Packaged notices |
|---|---|---|---|---|
'''
    (ROOT / 'THIRD_PARTY_NOTICES.md').write_text(preamble + '\n'.join(rows) + '\n')
    print(f'Recorded notices for {len(rows)} pinned Python packages.')


if __name__ == '__main__':
    generate()
