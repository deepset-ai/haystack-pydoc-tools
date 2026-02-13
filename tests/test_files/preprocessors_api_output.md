---
title: "PreProcessors"
id: preprocessors-api
description: "Preprocess your Documents and texts. Clean, split, and more."
slug: "/preprocessors-api"
---

<a id="document_splitter"></a>

## Module document\_splitter

<a id="document_splitter.DocumentSplitter"></a>

### DocumentSplitter

Splits long documents into smaller chunks.

This is a common preprocessing step during indexing. It helps Embedders create meaningful semantic representations
and prevents exceeding language model context limits.

The DocumentSplitter is compatible with the following DocumentStores:
- [Astra](https://docs.haystack.deepset.ai/docs/astradocumentstore)
- [Chroma](https://docs.haystack.deepset.ai/docs/chromadocumentstore) limited support, overlapping information is
  not stored
- [Elasticsearch](https://docs.haystack.deepset.ai/docs/elasticsearch-document-store)
- [OpenSearch](https://docs.haystack.deepset.ai/docs/opensearch-document-store)
- [Pgvector](https://docs.haystack.deepset.ai/docs/pgvectordocumentstore)
- [Pinecone](https://docs.haystack.deepset.ai/docs/pinecone-document-store) limited support, overlapping
   information is not stored
- [Qdrant](https://docs.haystack.deepset.ai/docs/qdrant-document-store)
- [Weaviate](https://docs.haystack.deepset.ai/docs/weaviatedocumentstore)

### Usage example

```python
from haystack import Document
from haystack.components.preprocessors import DocumentSplitter

doc = Document(content="Moonlight shimmered softly, wolves howled nearby, night enveloped everything.")

splitter = DocumentSplitter(split_by="word", split_length=3, split_overlap=0)
result = splitter.run(documents=[doc])
```

<a id="document_splitter.DocumentSplitter.__init__"></a>

#### DocumentSplitter.\_\_init\_\_

```python
def __init__(split_by: Literal["function", "page", "passage", "period", "word",
                               "line", "sentence"] = "word",
             split_length: int = 200,
             split_overlap: int = 0,
             split_threshold: int = 0,
             splitting_function: Callable[[str], list[str]] | None = None,
             respect_sentence_boundary: bool = False,
             language: Language = "en",
             use_split_rules: bool = True,
             extend_abbreviations: bool = True,
             *,
             skip_empty_documents: bool = True)
```

Initialize DocumentSplitter.

**Arguments**:

- `split_by`: The unit for splitting your documents. Choose from:
- `word` for splitting by spaces (" ")
- `period` for splitting by periods (".")
- `page` for splitting by form feed ("\f")
- `passage` for splitting by double line breaks ("\n\n")
- `line` for splitting each line ("\n")
- `sentence` for splitting by NLTK sentence tokenizer
- `split_length`: The maximum number of units in each split.
- `split_overlap`: The number of overlapping units for each split.
- `split_threshold`: The minimum number of units per split. If a split has fewer units
than the threshold, it's attached to the previous split.
- `splitting_function`: Necessary when `split_by` is set to "function".
This is a function which must accept a single `str` as input and return a `list` of `str` as output,
representing the chunks after splitting.
- `respect_sentence_boundary`: Choose whether to respect sentence boundaries when splitting by "word".
If True, uses NLTK to detect sentence boundaries, ensuring splits occur only between sentences.
- `language`: Choose the language for the NLTK tokenizer. The default is English ("en").
- `use_split_rules`: Choose whether to use additional split rules when splitting by `sentence`.
- `extend_abbreviations`: Choose whether to extend NLTK's PunktTokenizer abbreviations with a list
of curated abbreviations, if available. This is currently supported for English ("en") and German ("de").
- `skip_empty_documents`: Choose whether to skip documents with empty content. Default is True.
Set to False when downstream components in the Pipeline (like LLMDocumentContentExtractor) can extract text
from non-textual documents.

<a id="document_splitter.DocumentSplitter.warm_up"></a>

#### DocumentSplitter.warm\_up

```python
def warm_up()
```

Warm up the DocumentSplitter by loading the sentence tokenizer.

<a id="document_splitter.DocumentSplitter.run"></a>

#### DocumentSplitter.run

```python
@component.output_types(documents=list[Document])
def run(documents: list[Document])
```

Split documents into smaller parts.

Splits documents by the unit expressed in `split_by`, with a length of `split_length`
and an overlap of `split_overlap`.

**Arguments**:

- `documents`: The documents to split.

**Raises**:

- `TypeError`: if the input is not a list of Documents.
- `ValueError`: if the content of a document is None.

**Returns**:

A dictionary with the following key:
- `documents`: List of documents with the split texts. Each document includes:
- A metadata field `source_id` to track the original document.
- A metadata field `page_number` to track the original page number.
- All other metadata copied from the original document.

<a id="document_splitter.DocumentSplitter.to_dict"></a>

#### DocumentSplitter.to\_dict

```python
def to_dict() -> dict[str, Any]
```

Serializes the component to a dictionary.

<a id="document_splitter.DocumentSplitter.from_dict"></a>

#### DocumentSplitter.from\_dict

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> "DocumentSplitter"
```

Deserializes the component from a dictionary.

