# Forestry AI Core module
The Forestry AI Core module provides common functions for augmentation, tokenizing, encoding, and classification.  Aid for generative modelling is more geared towards structuring Azure AI pipelines or LLM orchestration preferred for large amounts of internal documentation.

## Semantic augmentation
The term semantic augmentation means that text is augmented with custom dimensions to help routing and the quality of responses from a generative model.  The augmentation process is a pipeline of directives:

- Augmentation
- Tokenizing
- Encoding 
- Classification

This module has **profiles** to simplify the construction of an augmentation pipeline that yields the input text with dimensions predicted by classification that often will include routing information.  Input text can be both a **question** and an **answer** comprising an adjacency pair but it may even be just answers that are neutral enough to be regarded as statements.

The first directive of augmentation would take the input and create a record plus predictions.  The record is a tuple containing the input text plus derived dimensions (metadata).  Predictions are a pool of possible dimensions procured from the classification directive.  Those prediction dimensions are what drive routing and help the generative LLM to resolve input.

The input "Varför har priskollektiv inte använts?" from Teams could have the following record:

| Key          | Value                     |
| ------------ | ------------------------- |
| text         | ...                       |
| source       | Teams                     |
| timestamp    | ...                       |
| user         | Monty                     |
| type         | Question                  |
| channel      | Kundtjänst Redovisning    |

There are more dimensions that could be hijacked knowing that the text comes from a particular Teams channel but the above is enough to understand how augmentation takes input and constructs a record.  Augmentation also has the responsibility for outbound predictions like:

| Key          | Value                                  |
| ------------ | -------------------------------------- |
| route        | redovisning, uppföljning, ...          |
| type         | adjacency pair, statement ...          |
| level        | 2-linjen, 3-linjen, projekt ...        |

The original input plus dimensions from augmentation and classification are routed onward.  Input is only enriched with helpful dimensions.

## Tokenizing
Tokenizing has only one purpose.  It creates numeric references for textual symbols where the references map to symbols in a model.  That is all.  The Swedish BERT model [KB/bert-base-swedish-cased](https://huggingface.co/KB/bert-base-swedish-cased) is trained on 3000M tokens.  The input "Varför har priskollektiv inte använts?" when tokenized basically becomes:

```
"[CLS]"        -> 101
"Varför"       -> 2339
"har"          -> 2003
"pris"         -> 8241
"##kollektiv"  -> 2075
"inte"         -> 1996
"använts"      -> 8857
"?"            -> 1029
"[SEP]"        -> 102
```

The assigned identifications are an array of numerical references to tokens in the model.  They are labels not numbers with magnitude or meaning.  ```1029``` is not bigger than ```102```.  ```1029``` is just a look-up key.  With a BERT style tokenizer there are some important tokens:

- Subwords (pris + ##kollektiv) keep the vocabulary smaller
- Special tokes ([CLS], [SEP]) provide structure
- Question marks or periods have corresponding tokens.

### BERT profile
The tokenizing pipeline directive defaults to a BERT profile.  A BERT tokenizer uses Word Piece tokenization.  Here is a good [reference](https://www.exxactcorp.com/blog/Deep-Learning/how-do-bert-transformers-work) with more detail.  BERT stands for Bidirectional Encoder Representations from Transformers used with  Natural Language Processing (NLP) tasks.  A Swedish‑optimized BERT models exist since the base English BERT struggles with Swedish morphology.

#### Chunking with overlap
BERT has built in chunking with overlap to handle long paragraphs what exceed a model's max token length.  Instead of truncating (i.e. ```truncation=True```) a sliding window can preserve context at chunk boundaries.  The default settings are starting point:

| Parameter    | Typical value             | Why                             |
| ------------ | ------------------------- | ------------------------------- |
| max_length   | model max e.g. 512        | Hard limit                      |
| stride       | 20-30% of max length      | Keeps continuity                |
| overlap      | max length - stride       | Context carryover               |

Here is an example:

```
from transformers import AutoTokenizer, AutoModel
import torch

model_name = "KB/bert-base-swedish-cased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

inputs = tokenizer(
    text,
    max_length=512,
    truncation=True,
    stride=128,
    return_overflowing_tokens=True,
    return_offsets_mapping=True,
    return_tensors="pt"
)
```

### Masks
Again the primary task when tokenizing is making tokens but a secondary spin-off is making masks:

- Attention
- Token type
- Special token

These binary masks (flags) guide the model during transformation layers.  The most important is the *attention* flags which tokens can be ignored i.e. padding.  The token type is for sentence pairing which is useful with adjacency pairs.  Special tokens may be ignored by the last mask.

## Encoding
The encoding directive is actually a series of forwarding calls inside the model to create *gut feelings* about a sentence.  Technically the actual product is aggregated vectors of all of the tokens in sentences.  These *gut feelings* are stacked together with the augmented dimensions.  Fine-tuning the encoding process is complicated (e.g. Quantification) and the default is to freeze the model.  Freezing means that the weights inside the neural network are not adjusted.  The input coming into encoding will always generate the same vector.  This is code snippet showing how to freeze:

```
model.eval() # dropout is disabled in evaluation mode
for param in model.parameters(): 
    param.requires_grad = False
```

### Embeddings
The first encoding step constructs token embeddings.  Embeddings let BERT *read* text.  BERT has 3 *input embeddings* where the output of each is aggregated into a final embedding.  The phases are:

1. Token embeddings
2. Segment (token‑type) embeddings
3. Position embeddings

The output is a vector per token.  The token embedding creates a rectangle of 768 (for BERT‑base) elements for each token.  This embedding wants to capture semantic meaning of subwords.  It deals with Swedish morphology and compounds.  The segment embedding creates a rectangle of increasing identifiers for each token in a segment ie. a sentence.  This tells BERT which sentence a token belongs to thereby letting BERT:

- Next‑sentence prediction (original BERT pre-training)
- Question‑answering
- Sentence‑pair classification

Lastly since transformers have no inherent sense of order forces BERT to inject absolute positional information.  This is crucial for Swedish, where word order affects meaning.  The fused embedding is what allows BERT later to understand intent, topic, sentiment, metadata, routing category etc.

### Transformers
The transformation layers make contextual embeddings from the input embeddings.  Training or shrinking the size of a model is very hard when the base BERT has 12 transformation layers.  This module does not have functions for quantization.  The output of transformation is a informative vector per token about context inside input.  This output has the peculiar name ```last_hidden_state``` and can be made with:

```
    with torch.no_grad():  # same as for-loop before
        outputs = model(**inputs)
        token_embeddings = outputs.last_hidden_state # (1, token count, hidden 768 vector)
```

### Pooling
After transformation the individual token embeddings must be consolidated into an sentence embedding (i.e. the dimensions apply to the input as a whole) to be stacked with custom dimensions.  The input "Varför har priskollektiv inte använts?" plus BERT's special tokens is 9 tokens in total.  The shape is a 2 dimensional array 9 wide and 768 deep.  Imagine each token embedding is a tiny *opinion* about the meaning of the sentence.  Mean‑pooling simply wants to average all these opinions to get one overall summary.  This is a one-liner in Python:

```
sentence_embedding = token_embeddings.mean(dim=1).squeeze(0)
```

Mean does:
- dim=1 gives an average across all tokens
- collapse the sequence of token vectors into one single vector
- the new vector is the average of all token embeddings

then squeeze does:
- removes the batch dimension if only one sentence is passed
- turns shape ```(1, 768)``` into ```(768)``` where 768 == hidden vector size of the model

There are other pooling kinds.  CLS is often weaker unless fine-tuned.  Max is sometimes noisy.

When stacking with custom dimensions the following might help to normalize:

```
sentence_embedding = torch.nn.functional.normalize(
    sentence_embedding,
    dim=0
)
```

### Stacking
The input is now a sentence embedding but the custom dimensions from the record have to be included otherwise the quality of classification is diminished.  The record is just a tuple with keys and names.  Each value needs to be transformed into an array of flags and each key has it's own logic.

```
import numpy as np

source_mapping = {
    "teams": np.array([1, 0, 0])
    "salesforce": np.array([0, 1, 0])
    "devops": np.array([0, 0, 1])
}

def from_binary(value: bool) -> np.array:
    return np.array([1.0 if value else 0.0])

def from_one_of(value, options):
    vector = np.zeros(len(options))
    vector[options.index(value)] = 1.0
    return vector

metadata_embedding = np.concatenate([
    source_mapping[record["source"]],
    from_binary(record["is_question"]),
    from_one_of(record["priority", ["low", "medium", "high"]])
])
```

With the metadata embedding a stack or concatenate can be done:
```
enriched_embedding = np.concatenate([
    text_embedding,
    metadata_embedding
])
```

## Classification
Using the default frozen model training happens during classification.  A deterministic approach lets the model be swappable.  This module can then be isolated to assisting with augmentation and tuning classification which is very CPU / GPU friendly (e.g. easy on a laptop).  When training the classifier needs evidence (i.e. what dimensions the pipeline produces).  Evidence is what is put on the y-axis with the enriched embedding on the x-axis during classification *fitting*.  

```
X = []
y = []

X.append(enriched_embedding)
y.append("redovisning")

X = np.vstack(X)
y = np.array(y)
```

Then the dataset is fitted:
```
from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

classifier.fix(X, y)
```

No deep learning required.

### Evaluating
To evaluate classification a prediction can be made:

```
x = np.concatenate([text_embedding, metadata_embedding]).reshape(1, -1)
classifier.predict(x)[0]
```

Hopefully, the predication for "Varför har priskollektiv inte använts?" should give "redovisning".  This methodology works well due to:

- Text embedding encodes **semantic meaning**
- Metadata encodes **situational context**
- Classifier learns **conditional behavior**
- Metadata can be tweaked without retraining the encoder
- Debugging is trivial (feature weights)

### Big picture
The core takeaway is that this module is not helping BERT or any other model.  This module gives the classifier the information BERT can not know (i.e. RAG).  Prediction is not limited to only one output and can be multi-label.

## Generative AI
Again this module isn't concerned with how the augmented input (e.g. input text + dimensions both defined and predicted) is used.  That said augmenting serves a purpose to either help routing, forward to generative LLM or even tasks (e.g. create a bug).  The outbound format of the augmented input is important.  This module will have functions for structuring output:

- clear or unambiguous dimension names
- consistent formatting e.g. separation of dimensions, input, instructions

With structure if the LLM is specialized (e.g. a handbook LLM) then outbound structure:

- reinforce context
- reduce hallucinations
- help the model stay in it's domain

### LoRA fine-tuning
Fine-tuning an LLM is only good when a domain model needs to follow highly specific workflows.  Also LoRA fine-tuning plays nice with question and answer adjacency pairs that need reasoning not just facts.  

### Orchestration
Orchestration is great at housing versioned facts and lookup.  Usually a general LLM fronts (e.g. Microsoft' Agentic Retrieval / semantic kernel) to find the right domain vector index, get top chucks, and prompt the LLM to answer only based on retrieved content and provide citations.  The basic flow is:

- Grab relevant documents (search index, vector storage etc.)
- Compress most relevant passages
- Feed 