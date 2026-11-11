Yamaya ContentFlow

AI-Powered Content Planning, Editorial Review & Repurposing Studio

About the Project

Yamaya ContentFlow is an AI-powered content workflow assistant designed to help digital publishers, independent creators, and small media teams plan, review, and repurpose content more efficiently.

Inspired by real content production and operational challenges experienced at Yamaya Afrique, a Nigerian digital publication focused on youth culture, lifestyle, and entertainment, the project aims to simplify repetitive content workflows through Python and generative AI.

The Problem

Content teams spend considerable time brainstorming ideas, developing content, reviewing drafts, extracting information from documents, and adapting existing material for different platforms.

For small teams with limited resources, these repetitive tasks can make content production more demanding and time-consuming.

Proposed Solution

Yamaya ContentFlow provides a modular application with three main workflows:

1. Content Ideation: Generates content ideas and develops selected concepts into social media content.
2. Editorial Review: Evaluates existing content for editorial quality, potentially unsupported claims, and areas requiring human verification.
3. Content Repurposing Studio: Transforms existing source material into different content formats while considering brand voice and source fidelity.

Current Features

1. Content Ideation

- Topic and target audience input.
- Content idea generation.
- Carousel and Reel development.
- Brand-specific tone and writing guidelines.

2. Editorial Review

- AI-assisted content assessment.
- Identification of potentially unsupported claims.
- Suggested editorial corrections.
- Human verification recommendations.

3. Content Repurposing

- Pasted text input.
- PDF and DOCX document processing.
- Image text extraction through OCR.
- AI-powered image analysis.
- Single-format and multi-format content generation.
- Source-fidelity instructions to reduce unsupported additions.

Supported Brands

- Yamaya Afrique
- ErikaL Naturals

Supported Output Formats

- Social media carousels
- Instagram Reels scripts
- Blog articles
- Newsletters
- Social media captions

Technology Stack

- Python: Application development and workflow logic.
- Google Gemini API: AI-powered content generation, editorial review, and image analysis.
- Google Colab: Development and testing environment.
- GitHub: Version control and project documentation.
- PyMuPDF and pypdf: PDF processing.
- python-docx: Word document processing.
- Pytesseract and Pillow: Image text extraction and image processing.

Project Architecture

The project uses a modular structure, with separate Python files responsible for different functions.

The main application ("app.py") connects the workflows, while supporting modules handle brand profiles, AI generation, editorial review, document processing, image analysis, and content repurposing.

Project Status

Currently in development.

Implemented and tested:

- Brand-specific content generation.
- Editorial review workflow.
- Source text processing.
- DOCX text extraction.
- PDF text extraction in standalone tests.
- Image OCR.
- Gemini Vision image analysis.
- Single-format and multi-format repurposing.
- End-to-end content repurposing pipeline.
- Integration of three workflows into the main application.

Document upload has been implemented in the main application but still requires verification in the Colab browser environment.

A unified graphical dashboard and further workflow improvements remain future development goals.

Important Limitations

- AI-generated content requires human editorial review before publication.
- AI-assisted editorial review does not independently establish factual or scientific accuracy.
- Generated content may occasionally introduce details not present in the original source.
- OCR can produce extraction errors depending on document quality.
- API availability and usage are subject to Gemini's applicable limits.

Learning Objectives

This project is helping me develop practical skills in:

- Python programming.
- Modular software development.
- Generative AI integration.
- Prompt engineering.
- Workflow automation.
- Document and image processing.
- Input validation and error handling.
- Application testing and debugging.
- Technical documentation.

Project Motivation

Yamaya ContentFlow is a practical learning and portfolio project developed to explore how AI automation can solve real content production challenges.

My goal is to develop the technical skills needed to build useful AI-powered automation systems for businesses, publishers, and creative teams.

Developer: Alex Esther
Project: Koya AI Automation Developer Portfolio
