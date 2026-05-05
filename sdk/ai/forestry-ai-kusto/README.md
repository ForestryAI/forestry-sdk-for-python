# NPL to Kusto (KQL)
Kusto is among other things a query language used for Azure Monitor and Azure Data Lake.  This module helps a natural language be translated to Kusto.  Forestry does not at the time of writing use Azure Data Lake but given the limitations of BI it might be more user-friendly to chat about metrics and events as aggregations.

## High-level
Other studies (see references **1**, **2**) have used zero-short and few-shot *learning* on LLMs with varying accuracy depending on the underlying model (e.g. gpt 4 versus 3).  Few-shot has proven the better methodology.  However, this is not *learning* rather a term that stuck.  The model is frozen.  The studies rely on well structured prompts (e.g. not just user input), pre-trained statistical knowledge and pattern completion.  It is not learning rather **pattern imitation**.  The model is *reminded* on each call.

A more robust approach is *training* with a core AI pipeline

## Training
The schemas even for tracing and metrics from Azure Monitor har stable.  Even statistical information in data lakes will have a schema.  Fine-tuning or adapter will outperform real-time patter completion.  Prompting (i.e. taking input into a structured format) is very important where a pipeline could infer intent (element, filters etc.).  LoRA (Low-Rank Adaptation) lets the base model be frozen, only add small trainable matrices and **teach** the model how to behave per task.

## References
These references are not exhaustive.

1. Malmö university - Leveraging Generative AI to Translate Natural Language into Kusto Queries for Connected Car Network Monitoring [1](http://www.diva-portal.org/smash/get/diva2:1905769/FULLTEXT01.pdf)
2. Microsoft NL2KQL: From Natural Language to Kusto Query [2](https://github.com/microsoft/NL2KQL?tab=readme-ov-file)