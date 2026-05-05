from enum import Enum
import Forestry.core.settings as settings

class Model:
    """Model is an enumeration of values for rag models
    
    """
    BERT_DEFAULT_MODEL = "google-bert/bert-base-uncased"
    """Default BERT model for RAG tasks"""