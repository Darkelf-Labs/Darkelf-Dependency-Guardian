#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from logger import startup, info, success, failure
from core.doctor import GuardianDoctor
from core.scanner import ProjectScanner
from core.compatibility import CompatibilityEngine, print_report
from core.reporter import Reporter
from core.updater import GuardianUpdater
from core.package_manager import PackageManagerDetector


VERSION="1.1.0"
def main():
    startup("Darkelf Dependency Guardian", VERSION)
    p=argparse.ArgumentParser(prog="guardian")
    s=p.add_subparsers(dest="cmd")
    [s.add_parser(x) for x in ("scan","doctor","audit","verify","compatibility","report","update")]
    a=p.parse_args()
    if a.cmd=="scan":
        pr=ProjectScanner(".").scan();print(pr);return 0
    if a.cmd=="doctor":
        GuardianDoctor().run();return 0
    if a.cmd=="audit":
        pm = PackageManagerDetector(".").detect()
        r = pm.audit()
        print(r.stdout)
        return r.exit_code
    if a.cmd=="verify":
        pm = PackageManagerDetector(".").detect()

        for fn in (pm.lint, pm.build):
            r = fn()
            if not r.success:
                return r.exit_code

        success("Verification complete")
        return 0
    if a.cmd=="compatibility":
        rep=CompatibilityEngine().check(ProjectScanner(".").scan());print_report(rep);return 0
    if a.cmd=="report":
        rep=CompatibilityEngine().check(ProjectScanner(".").scan());rp=Reporter();rp.write_json(rep);rp.write_markdown(rep);rp.write_html(rep);rp.write_sarif(rep);return 0
    if a.cmd=="update":
        GuardianUpdater(".").print_report();return 0
    p.print_help();return 0
if __name__=="__main__":
    raise SystemExit(main())
