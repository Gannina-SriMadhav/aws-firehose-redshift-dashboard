\# AWS Firehose Redshift Dashboard



An AWS Data Engineering project that collects application events using Amazon Data Firehose, stages the data in Amazon S3, loads it into Amazon Redshift Serverless, and displays analytics through a Streamlit dashboard.



\## Architecture



Python / AWS CLI

&#x20;       ↓

Amazon Data Firehose

&#x20;       ↓

Amazon S3

&#x20;       ↓

Amazon Redshift Serverless

&#x20;       ↓

Streamlit Dashboard



\## AWS Services Used



\- Amazon Data Firehose

\- Amazon S3

\- Amazon Redshift Serverless

\- AWS IAM

\- Amazon CloudWatch

\- Streamlit

\- Python

\- AWS CLI



\## Database



Schema:



`analytics`



Table:



`analytics.events`



Columns:



\- event\_id

\- event\_type

\- user\_id

\- page

\- event\_time



\## Dashboard



The dashboard displays:



\- Total Events

\- Unique Users

\- Event Types

\- Pages

\- Event Type Distribution

\- Page Visit Distribution

\- Events by User

\- Events Over Time

\- Recent Events



\## How to Run



Install dependencies:



```bash

pip install -r requirements.txt

