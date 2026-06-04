# AIMA – AI Incident Management Assistant

## Overview

AIMA is an AI-powered incident management platform built using:

* LangGraph
* LangChain Tools
* ChromaDB
* Streamlit

The platform helps organizations automatically:

* Classify employee incidents
* Retrieve historical memory
* Calculate incident priority
* Generate responses
* Provide transparent reasoning traces

---

## Features

### LangGraph Workflow

1. Memory Retrieval
2. Incident Classification
3. Priority Calculation
4. Tool Execution
5. Response Generation
6. Memory Storage

### ChromaDB Memory

Persistent vector memory:

* Historical incidents
* Context retrieval
* Continuous learning

### Streamlit Dashboard

* Incident submission
* Classification display
* Priority display
* Memory visibility
* Reasoning transparency

---

## Installation

pip install -r requirements.txt

---

## Run Application

streamlit run app.py

---

## Example Incidents

* Laptop not connecting to VPN.
* Salary not credited this month.
* Requesting annual leave approval.
* Unable to access HR portal.
* Manager harassment complaint.

---

## Architecture

User → LangGraph → ChromaDB → Tool → Response → Memory Save

---

## Future Enhancements

* LLM integration
* Ticketing integration
* Dashboard analytics
* Escalation engine
* Multi-agent architecture
