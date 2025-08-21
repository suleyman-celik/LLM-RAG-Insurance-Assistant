# Bitext - Insurance Tagged Training Dataset for LLM-based Virtual Assistants

## Overview

This hybrid synthetic dataset is designed to be used to fine-tune Large Language Models such as **GPT**, **Mistral**, and **OpenELM**, and has been generated using Bitext’s **NLP/NLG technology** and **automated Data Labeling (DAL)** tools.  

The goal is to demonstrate how **Verticalization / Domain Adaptation** for the **insurance** sector can be easily achieved using Bitext’s **two-step approach to LLM Fine-Tuning**.  
➡️ More details: *From General-Purpose LLMs to Verticalized Enterprise Models*

### Specifications

- **Use Case**: Intent Detection  
- **Vertical**: Insurance  
- **39 intents** assigned to **17 categories**  
- **39,000 question/answer pairs** (~1000 per intent)  
- **100 entity/slot types**  
- **10 types of language generation tags**  

The categories and intents are derived from Bitext's extensive industry datasets, ensuring relevance and applicability across diverse insurance contexts.  

---

## Dataset Token Count

- **Total tokens**: ~5.13 million  
- **Columns contributing tokens**: `instruction` and `response`  

This corpus is designed to train **sophisticated LLMs** for:  
- Conversational AI  
- Question Answering  
- Virtual Assistant tasks in the **insurance domain**  

---

## Dataset Fields

Each entry in the dataset contains:

- **tags**  
- **instruction** → user request from the insurance domain  
- **category** → high-level semantic category for the intent  
- **intent** → specific intent of the instruction  
- **response** → example of an expected virtual assistant reply  

---

## Categories & Intents

### AUTO_INSURANCE
- `information_auto_insurance`

### CLAIMS
- `accept_settlement`  
- `file_claim`  
- `negotiate_settlement`  
- `receive_payment`  
- `reject_settlement`  
- `track_claim`  

### COMPLAINTS
- `appeal_denied_insurance_claim`  
- `dispute_invoice`  
- `file_complaint`  

### CONTACT
- `agent`  
- `customer_service`  
- `human_agent`  
- `insurance_representative`  

### COVERAGE
- `change_coverage`  
- `check_coverage`  
- `downgrade_coverage`  
- `upgrade_coverage`  

### ENROLLMENT
- `buy_insurance_policy`  
- `cancellation_fees`  
- `cancel_insurance_policy`  
- `compare_insurance_policies`  

### GENERAL_INFORMATION
- `general_information`  

### HEALTH_INSURANCE
- `information_health_insurance`  

### HOME_INSURANCE
- `information_home_insurance`  

### INCIDENTS
- `report_incident`  
- `schedule_appointment`  

### LIFE_INSURANCE
- `information_life_insurance`  

### PAYMENT
- `check_payments`  
- `payment_methods`  
- `pay`  
- `report_payment_issue`  
- `schedule_payments`  

### PET_INSURANCE
- `information_pet_insurance`  

### POLICY
- `change_personal_details`  

### QUOTE
- `calculate_insurance_quote`  
- `check_rates`  

### RENEW
- `renew_insurance_policy`  

### TRAVEL_INSURANCE
- `information_travel_insurance`  

---

## Entities

The dataset covers **100+ entities**, examples include:

- `{{WEBSITE_URL}}` → common with most intents  
- `{{INSURANCE_TYPE}}` → e.g., *change_coverage*, *check_payments*  
- `{{INSURANCE_POLICY_SECTION}}` → e.g., *buy_insurance_policy*, *compare_insurance_policies*  
- `{{PAYMENTS_OPTION}}` → e.g., *check_payments*  
- `{{TIME_FRAME}}` → e.g., *file_complaint*  

These entities ensure the dataset can train models to understand and process a **wide range of insurance-related queries**.  

---
