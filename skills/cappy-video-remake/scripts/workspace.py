"""Locate the Cappy production workspace; optionally forward to its CLI."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', metavar='VIDEO_URL', help='Run the existing studio CLI with a reference URL')
    args = parser.parse_args()
    root = Path(os.environ.get('CAPPY_WORKSPACE', 'D:/workspace/Aiagentbot')).expanduser().resolve()
    if not (root / 'remake_studio').is_dir():
        parser.error(f'Cappy workspace not found at {root}; set CAPPY_WORKSPACE to the production project')
    if args.run:
        return subprocess.call([sys.executable, '-m', 'remake_studio.cli', args.run], cwd=root)
    print(root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
