# Accessibility auditor CI/CD workflow

Configurable GitHub Action to automatically run accessibility audits on mobile web applications and post findings as comments on pull requests.

Requires a GitHub repository with a pull request workflow and a mobile web application that can be accessed via a URL.


## Follow the steps below to set up the action in your repository.

# Step 1:

Give permissions to the workflow to read and write to the repository following the steps on images below:

    Go to settings in your repository

![img_1.png](docs/assets/github_repository_settings.png)

    On the sidebar menu on your left, click on Actions > General and scroll down to the "Workflow permissions" section.

![img_2.png](docs/assets/github_sidebar_actions_general.png)

    Select the option "Read and write permissions" and check the box "Allow GitHub Actions to create and approve pull requests".

![img_3.png](docs/assets/github_workflow_permissions_allow.png)

# Step 2:

    Create a new workflow file in your repository's `.github/workflows` directory, for example, `a11y-audit.yml`.

![img.png](docs/assets/github_workflow_yaml_configuration.png)

# Step 3:

    Copy the following code into your workflow file, replacing `your-organization` with your GitHub organization or username, and `your-repo` with the name of your repository, and leave kotlin or swift files as default, or add/remove file types to monitor for changes.


```yaml
name: Accessibility CI

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    paths:
      - '**.kt'
      - '**.swift'

jobs:
  run-audit:
    uses: wizeline/wz-lab-mobile-a11y-guardian/.github/workflows/reusable_audit.yml@main
    secrets: inherit
```

 ## Additional configuration options

you can also replace default inputs with your own values:

    Available inputs:
        provider: The provider to use for the accessibility audit. Default is 'grok'. available options are 'grok' and 'gemini'.
        model: The model to use for the accessibility audit. Default is 'qwen/qwen3.8-27b'.

Example:
```yaml
jobs:
  run-audit:
    uses: wizeline/wz-lab-mobile-a11y-guardian/.github/workflows/reusable_audit.yml@main
    with:
      provider: 'gemini'
      model: 'gemini-2.5-flash'
    secrets: inherit
    
```

You can choose the <span style="color: orange;">branches</span> where the workflow will run, change the <span style="color: orange;">types</span> of events that trigger the workflow, or specify the <span style="color: orange;">paths</span> of the file types to monitor for changes. The default configuration is set to run on pull requests that modify Kotlin files (`.kt`) or Swift files (`.swift`) in the `main`, `develop`, or any `feature/**` branches.

```yaml
name: Accessibility CI

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    paths:
      - '**.kt'
      - '**.swift'
    branches:
      - main
      - develop
      - feature/**
```


There is a compact skill for free tier accounts tests, default value is <span style="color: orange;">true</span>, in case you want to use multi skill approach you can change the <span style="color: orange;">use_compact_skill</span> input to <span style="color: orange;">false</span> as below

```yaml
jobs:
  run-audit:
    uses: wizeline/wz-lab-mobile-a11y-guardian/.github/workflows/reusable_audit.yml@main
    with:
      use_compact_skill: false
    secrets: inherit
```