# Execution Guide

## Running the Data Preprocessing Pipeline Locally

### Prerequisites
1. Ensure you have Python 3.x installed.
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Steps to Run the Pipeline
1. Clone the repository:
   ```bash
   git clone https://github.com/Deligent18/sentinel-XAI.git
   cd sentinel-XAI
   ```
2. Run the preprocessing script:
   ```bash
   python preprocessing.py
   ```

## Running the Data Preprocessing Pipeline via GitHub Actions

### Workflow Configuration
1. Ensure you have a `.github/workflows/preprocess.yml` file in your repository.
2. The workflow file should include the following steps:
   ```yaml
   name: Data Preprocessing

   on:
     push:
       branches:
         - main

   jobs:
     preprocess:
       runs-on: ubuntu-latest
       steps:
       - name: Checkout code
         uses: actions/checkout@v2

       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.x'

       - name: Install dependencies
         run: |
           pip install -r requirements.txt

       - name: Run preprocessing
         run: |
           python preprocessing.py
   ```
3. Commit and push your changes. The workflow will automatically trigger on pushes to the main branch.

## Additional Notes
- Ensure your data files are correctly placed in the expected directories before running the pipeline.
- Check the logs in GitHub Actions for any errors during the run.