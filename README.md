---
title: Datasets Convertor
emoji: 👁
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: 5.20.0
app_file: app.py
pinned: false
short_description: Support by Parquet, CSV, Jsonl, XLS
---
![GitHub Repo stars](https://img.shields.io/github/stars/canstralian/Datasets-Convertor?style=social)
![GitHub forks](https://img.shields.io/github/forks/canstralian/Datasets-Convertor?style=social)
![GitHub issues](https://img.shields.io/github/issues/canstralian/Datasets-Convertor)
![GitHub last commit](https://img.shields.io/github/last-commit/canstralian/Datasets-Convertor)

[![HF Space](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?logo=huggingface)](https://huggingface.co/spaces/whackthejacker/Datasets-Convertor)
![HF SDK](https://img.shields.io/badge/SDK-Gradio%205.20.0-blue?logo=python)
[![Apache 2.0 License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)

# Datasets Converter

**Datasets Converter** is a tool for migrating datasets between different platforms, including GitHub, Hugging Face, Kaggle, and Google Colab Notebooks. It simplifies dataset transfers for seamless integration into AI/ML workflows.

## Features

- Convert and migrate datasets between:
  - **GitHub** → **Hugging Face**
  - **GitHub** → **Kaggle**
  - **GitHub** → **Google Colab**
- Supports multiple dataset formats (CSV, JSON, Parquet, etc.).
- Automated metadata handling and versioning.
- CLI and API support for easy automation.

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/canstralian/Datasets-Convertor.git
cd Datasets-Convertor
pip install -r requirements.txt

Usage

CLI Usage

python convert.py --source github --destination huggingface --repo "https://github.com/user/repo"

API Usage (FastAPI)

Start the API:

uvicorn app:app --host 0.0.0.0 --port 8000

Example request:

curl -X POST "http://localhost:8000/convert" -H "Content-Type: application/json" \
     -d '{"source": "github", "destination": "huggingface", "repo": "https://github.com/user/repo"}'

Roadmap
   •   Add support for more dataset sources (Google Drive, S3, etc.).
   •   Enhance error handling and logging.
   •   Implement dataset validation and transformation features.

Contributing

Contributions are welcome! Please open an issue or submit a pull request.

License

This project is licensed under the Apache License 2.0.

Let me know if you need any adjustments!