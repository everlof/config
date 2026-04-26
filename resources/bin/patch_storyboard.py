#!/usr/bin/env python3
"""
convert_storyboard_to_code.py
---------------------------------
Helper that turns a *fresh* storyboard‑based Swift iOS “App” template
(Xcode 13 → 15) into a 100 % programmatic UI project.

Changes performed
=================
✔  Deletes **Main.storyboard** / **Main.storyboardc** from disk *and* from
   the Xcode project file
✔  Removes **INFOPLIST_KEY_UIMainStoryboardFile** build‑setting rows so they
   don’t creep back at build time
✔  Cleans storyboard entries from *Info.plist* / the scene manifest
✔  Patches **SceneDelegate.swift** *or* **AppDelegate.swift** (never both):
   • If your project uses scenes (default since iOS 13), only SceneDelegate is
     modified.
   • If no SceneDelegate is present, AppDelegate gets the window setup so the
     app still launches on iOS 12 and earlier.
✔  Leaves **LaunchScreen.storyboard** untouched – still required by Apple.

Usage
-----
```bash
python convert_storyboard_to_code.py /path/to/MyApp
# or, if your initial view controller is called something else
python convert_storyboard_to_code.py /path/to/MyApp --root-vc HomeVC
```

Limitations
-----------
* Meant for an untouched template.  For heavily customised project files you
  might have to do a final manual clean in Xcode’s *File Inspector*.
* Swift‑only for now – ping me if you need Objective‑C.
* iOS only (no tvOS/macOS yet).
"""
from __future__ import annotations

import argparse
import plistlib
import re
import shutil
import sys
from pathlib import Path
from typing import Tuple


# ────────────────────────────── helpers ──────────────────────────────

def find_xcodeproj(root: Path) -> Tuple[Path, str]:
    """Return the *.xcodeproj* path and project name inside *root*."""
    for entry in root.iterdir():
        if entry.suffix == ".xcodeproj":
            return entry, entry.stem
    sys.exit("❌  No .xcodeproj found in the supplied directory.")


def remove_storyboard_files(project_root: Path, project_name: str) -> None:
    """Delete Main.storyboard / .storyboardc bundles if they exist."""
    candidates = [
        project_root / project_name / "Main.storyboard",
        project_root / project_name / "Base.lproj" / "Main.storyboard",
        project_root / project_name / "Main.storyboardc",
        project_root / project_name / "Base.lproj" / "Main.storyboardc",
    ]
    for path in candidates:
        if path.exists():
            (shutil.rmtree if path.is_dir() else path.unlink)()
            print(f"🗑️  Deleted {path.relative_to(project_root)}")


def patch_info_plist(plist_path: Path) -> None:
    with plist_path.open("rb") as fp:
        data = plistlib.load(fp)

    changed = False
    # Pre‑iOS 13 storyboard key
    if data.pop("UIMainStoryboardFile", None):
        changed = True

    # Scene manifest (iOS 13+)
    manifest = data.get("UIApplicationSceneManifest", {})
    scenes = manifest.get("UISceneConfigurations", {})
    for configs in scenes.values():
        for cfg in configs:
            if cfg.pop("UISceneStoryboardFile", None):
                changed = True

    if changed:
        with plist_path.open("wb") as fp:
            plistlib.dump(data, fp)
        print(f"✏️  Patched {plist_path.name}")
    else:
        print("ℹ️  Info.plist already clean – skipping")


# ─────────────────────────── delegates patching ───────────────────────────

CONNECT_BLOCK_PATTERN = (
    r"func scene\([^)]*\)\s*{[^}]*}"  # willConnectTo in SceneDelegate
)

LAUNCH_BLOCK_PATTERN = (
    r"func application\([^)]*didFinishLaunchingWithOptions[^)]*\)\s*{[^}]*}"
)

CONNECT_TEMPLATE = (
    """func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {{
            guard let windowScene = (scene as? UIWindowScene) else {{ return }}
            window = UIWindow(windowScene: windowScene)
            window?.rootViewController = {root_vc}()
            window?.makeKeyAndVisible()
    \n"""
)

LAUNCH_TEMPLATE = (
    """func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {{
            window = UIWindow(frame: UIScreen.main.bounds)
            window?.rootViewController = {root_vc}()
            window?.makeKeyAndVisible()
            return true
    \n"""
)


def ensure_window_property(source: str, class_keyword: str) -> str:
    """Insert a `var window: UIWindow?` property if missing."""
    if "var window: UIWindow?" not in source:
        return source.replace(
            f"class {class_keyword}:",
            f"class {class_keyword}: UIResponder, {class_keyword[:-8]} {{\n    var window: UIWindow?\n",
            1,
        )
    return source


def patch_swift_file(path: Path, pattern: str, replacement: str, class_keyword: str) -> None:
    if not path.exists():
        return
    original = path.read_text()
    patched = re.sub(pattern, replacement, original, flags=re.S)
    patched = ensure_window_property(patched, class_keyword)

    if patched != original:
        path.write_text(patched)
        print(f"✏️  Patched {path.name}")


# ────────────────────────── project file cleanup ──────────────────────────

def strip_storyboard_from_pbxproj(pbxproj_path: Path) -> None:
    lines = pbxproj_path.read_text().splitlines(keepends=True)
    cleaned = [
        l
        for l in lines
        if "Main.storyboard" not in l and "INFOPLIST_KEY_UIMainStoryboardFile" not in l
    ]
    if len(cleaned) != len(lines):
        pbxproj_path.write_text("".join(cleaned))
        print(
            f"✏️  Removed storyboard refs from {pbxproj_path.relative_to(pbxproj_path.parent.parent)}"
        )
    else:
        print("ℹ️  No storyboard refs in project file – skipping")


# ────────────────────────────────── main ──────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Convert storyboard template to code‑only UI.")
    parser.add_argument("project_dir", help="Folder that contains *.xcodeproj* (open in Finder)")
    parser.add_argument("--root-vc", default="ViewController", metavar="CLASS", help="Root UIViewController class")
    args = parser.parse_args()

    project_root = Path(args.project_dir).expanduser().resolve()
    if not project_root.is_dir():
        sys.exit("❌  project_dir must be a directory (the one you normally open in Finder)")

    xcodeproj, proj_name = find_xcodeproj(project_root)
    print(f"🔍  Project detected: {proj_name}\n")

    remove_storyboard_files(project_root, proj_name)

    # Locate Info.plist
    for cand in [
        project_root / proj_name / "Info.plist",
        project_root / f"{proj_name}-Info.plist",
        project_root / proj_name / f"{proj_name}/Info.plist",
    ]:
        if cand.exists():
            patch_info_plist(cand)
            break
    else:
        print("⚠️  No Info.plist found – skipping")

    scene_delegate = project_root / proj_name / "SceneDelegate.swift"
    if scene_delegate.exists():
        patch_swift_file(
            scene_delegate,
            CONNECT_BLOCK_PATTERN,
            CONNECT_TEMPLATE.format(root_vc=args.root_vc),
            "SceneDelegate",
        )
    else:
        # Pre‑iOS13 template – patch AppDelegate instead
        app_delegate = project_root / proj_name / "AppDelegate.swift"
        patch_swift_file(
            app_delegate,
            LAUNCH_BLOCK_PATTERN,
            LAUNCH_TEMPLATE.format(root_vc=args.root_vc),
            "AppDelegate",
        )

    strip_storyboard_from_pbxproj(xcodeproj / "project.pbxproj")

    print("\n✅  All done! Clean (⇧⌘K) and build the project in Xcode.")


if __name__ == "__main__":
    main()
