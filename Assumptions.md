# Document Processing System

## Overview
System for processing CV documents in multiple formats to build knowledge base (RAG).

## Supported Formats
* Word (.docx, .doc)
* PDF
* Plain text
* Markdown
* JSON
## Key Features
* Multi-format document ingestion
* Text extraction and normalization
* Knowledge base indexing
* RAG (Retrieval-Augmented Generation) integration

## Assumptions
- Documents are valid CV files
- Encoding is UTF-8 compatible
- File sizes are within processing limits
- PDF documents are readable and extractable
- PDF password protection is not required
- System operates as multi-agent architecture
- Agents communicate asynchronously
- Each agent has defined responsibility scope
- Agent for document reading and processing
- Agent for candidate skill extraction
- Agent for team composition proposals based on required skills
- HR department accesses system via simple web interface
- Users can search candidates by required skills
- Users can compose entire teams based on specified skills
- Web interface is user-friendly and intuitive
- System includes retry mechanisms for failed operations
- Anti-hallucination measures implemented in agent responses
- Model temperature set to 0 for deterministic outputs
- Unknown answers return "I don't know" response instead of speculation

## Proposed Technologies
* **Language**: Python
* **Web Framework**: Django
* **Vector Database**: Chroma or FAISS
* **Hosting**: Local deployment with WSL (Windows Subsystem for Linux) option

## User Interface
- The web interface will use the Bootstrap framework for styling to ensure a clean and modern look.
- The main screen of the application will feature a navigation bar with three main sections (tabs):
  1.  **List All CVs**: A view that displays all uploaded documents and their processing status.
  2.  **Upload CV**: The existing interface for uploading new CV documents.
  3.  **Team Composition**: The interface for generating team proposals based on required skills.
