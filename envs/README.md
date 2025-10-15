# Interactive Environment Setup

This document outlines the setup process for the interactive environment used in our dynamic interactive evaluation. The environment relies on the following components:

*   **Display Server:** Xvfb for GUI operations.
*   **Web Browser:** Chrome for Testing, along with its corresponding ChromeDriver.
*   **Web Framework:** A Next.js application.

## Chrome Installation

To install Chrome for Testing and the corresponding ChromeDriver, execute the following script:

```bash
bash envs/google_chrome.sh
```

**Important:** This script will remove any existing installations of Google Chrome and ChromeDriver on your system. If you wish to keep your current Chrome installation, you will need to modify the script to bypass the uninstallation steps.

## Xvfb Installation

Installation scripts are provided for different platforms due to variations in package managers.

### CentOS

To install Xvfb and its dependencies on CentOS, run the following command:

```bash
bash envs/envs_centos.sh
```

### Ubuntu

The setup script for Ubuntu is currently under development. Please check back later for updates.

### Docker

A Docker-based setup is also in progress. Please check back later for updates.

## Next.js Application Setup

### Prerequisites

Before you begin, ensure you have Node.js and npm installed. You can find installation instructions [here](https://nodejs.org/en/download). Our experiments were conducted using Node.js v22.17.0 and npm v11.4.2.

### Setup Script

Once Node.js and npm are installed, run the following command to set up the Next.js application:

```bash
bash envs/set_up_nextjs_env.sh workspace/workspace_<worker_id>
```

The `<worker_id>` parameter is a zero-based index for the worker instance (e.g., 0, 1, 2, ...). If you plan to run the evaluation with multiple workers, you must create a separate environment for each one, using consecutive worker IDs.

During the setup process, you may be prompted to configure some Next.js settings. Please accept the default options for all prompts.