# 🛡️ Darkelf Dependency Guardian

**Framework-aware dependency compatibility analysis and safe update recommendations.**

Darkelf Dependency Guardian helps developers determine **whether dependency updates are safe before installing them**. Instead of recommending every available update, Guardian analyzes project compatibility rules and identifies updates that may introduce breaking changes.

---

## Features

- 🔍 Detect outdated dependencies
- 🛡️ Framework-aware compatibility analysis
- 📦 Supports npm, pnpm, Yarn, and Bun
- ⚙️ Automatic package manager detection
- 🔄 Safe update recommendations
- 💾 Automatic rollback before updates
- 📋 Project validation and health checks
- 📊 JSON, Markdown, HTML, and SARIF reports
- 🚀 GitHub Actions integration
- 🧩 Extensible rule engine for framework compatibility

---

## Supported Frameworks

- Next.js
- React
- Vue
- Angular
- Svelte
- Astro
- Remix
- Express
- NestJS
- Vite
- Electron
- Node.js

Additional frameworks can be added by creating new rule files.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Darkelf-Labs/Darkelf-Dependency-Guardian.git
cd Darkelf-Dependency-Guardian
```

---

## Usage

### Scan Project

```bash
guardian scan
```

### Validate Project

```bash
guardian validate
```

### Dependency Health Report

```bash
guardian doctor
```

### Safe Update Analysis

```bash
guardian update
```

---

## Project Structure

```
guardian.py
core/
    scanner.py
    validator.py
    compatibility.py
    rules_engine.py
    updater.py
    rollback.py
    reporter.py
    doctor.py
    package_manager/
rules/
.github/
```

---

## Reports

Guardian can generate reports in multiple formats:

- Markdown
- JSON
- HTML
- SARIF

These reports are suitable for local development and CI/CD pipelines.

---

## GitHub Actions

Guardian integrates easily into GitHub Actions to analyze dependency compatibility on every push and pull request.

Example:

```yaml
- name: Dependency Scan
  run: guardian doctor
```

---

## Roadmap

- Additional framework rule sets
- Improved semantic version analysis
- Selective package updates
- Dependency graph visualization
- Plugin system
- Expanded reporting capabilities

---

## License

MIT License

---

## About Darkelf Labs

Darkelf Dependency Guardian is part of the **Darkelf Labs** ecosystem of open-source developer and security tools focused on improving software reliability, privacy, and secure development workflows.
