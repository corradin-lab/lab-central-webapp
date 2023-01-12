# Python data analysis project structure template

## Introduction

This is a suggested project setup for a data analysis project. It uses open source projects to help you streamline data analysis workflow, maintain a sane and sensible folder structure, and follow best practices. Specifically, it uses:
- [Poetry](https://python-poetry.org/) for environment and dependencies management
- [Nbdev](https://nbdev.fast.ai/) and [LineaPy](https://github.com/LineaLabs/lineapy) for seamless transitions from messy, exploratory Jupyter notebooks to reusable code and packages with beautiful documentation
- [Kedro](https://github.com/kedro-org/kedro) for datasource management via data catalogs and reproducible/visualizable pipelines
- [Prefect](https://www.prefect.io/) to orchestrate and schedule pipelines, with retries and complex error handling

... and other modern utility tools like linting with [ruff](https://github.com/charliermarsh/ruff), code coverage with [slipcover](https://github.com/plasma-umass/slipcover)

## Getting started

### Prerequisite

You need to have [Poetry](https://python-poetry.org/) installed globally and Python >=3.8,<3.11

### Setup steps

1. Click on the `Use this template` button to create your own repository
<img width="1168" alt="image" src="https://user-images.githubusercontent.com/25307953/211792569-0271a06f-c2b3-432a-ad7e-3cd9f239bd34.png">
<img width="752" alt="image" src="https://user-images.githubusercontent.com/25307953/211794193-6d3c6439-18c0-4516-9c30-24f4b7c8bfd2.png">

2. Clone your repo locally using `git clone <repo url>`

3. Edit values in `change-my-values.yaml`, `project_name` should be your repository's name
<img width="434" alt="image" src="https://user-images.githubusercontent.com/25307953/211793460-8388650d-09ec-4366-b99d-0f3b9bfa667e.png">


4. Run the following commands
```
python create-repository.py
poetry shell
make install-packages
make reset-project
```

<details>
<summary><b>Example repository structure when finished</b></summary>

```
.
├── conf
│   ├── base
│   ├── local
│   └── README.md
├── create-repository.py
├── data
│   ├── 01_raw
│   ├── 02_intermediate
│   ├── 03_primary
│   ├── 04_feature
│   ├── 05_model_input
│   ├── 06_models
│   ├── 07_model_output
│   └── 08_reporting
├── docs
│   └── source
├── kedro-answers.yml
├── LICENSE
├── logs
├── Makefile
├── MANIFEST.in
├── notebooks
│   ├── analyses
│   ├── exploratory
│   ├── generate_figures
│   └── package
├── poetry.lock
├── _proc
│   ├── 00_core.ipynb
│   ├── _docs
│   ├── index.ipynb
│   ├── nbdev.yml
│   ├── _quarto.yml
│   └── styles.css
├── _pyproject.toml
├── pyproject.toml
├── README_kedro.md
├── README.md
├── settings.ini
├── setup.py
└── src
    ├── requirements.txt
    ├── setup.py
    ├── test_package_project
    └── tests
```
</details>
