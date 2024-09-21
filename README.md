
# Manuscript Management Server

This repository contains the backend for the Manuscript Management system, built using FastAPI. The system allows for efficient management of reviewers, papers, and manuscripts, with support for file uploads. It includes advanced features for matching manuscripts to reviewers based on content similarity, ensuring a streamlined and accurate review process.


### Key Features:
- Reviewer and Manuscript Management: Seamlessly handle operations related to manuscripts, reviewers, and papers.

- Key Phrase Extraction: Utilizes the KeyBERT model to extract meaningful key phrases from the manuscript's title and abstract.

- Content Similarity Matching: Implements the Jaccard similarity model to calculate and assign mean similarity scores based on manuscript_id and reviewer_id, enhancing reviewer assignment accuracy.

- File Upload Capabilities: Allows for file uploads to manage manuscript documents directly.


## API Reference

#### POST items

```https
  POST http://localhost:8081/api/extract
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `table_name` | `string` | **Required**. Mention table_name to retrieve mean similarity|
| `file` | `File` | **Required**. Input File|

## Tech Stack

**Server:** FastAPI

**Database:** PostgreSQL

## Getting Started

### Clone the Repository:

```bash
git clone https://github.com/Gaurav098766/manuscript
cd manuscript
```

### Set Up a Virtual Environment
- For Windows:
```bash
pip install virtualenv
python -m venv myenv
myenv\Scripts\activate
```

- For Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### Install Requirements
```bash
pip install -r requirements.txt
```

### Run the FastAPI Server
 ```bash
py runserver.py
```
