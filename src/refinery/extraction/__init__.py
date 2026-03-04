"""Multi-strategy extraction: FastText, Layout (Docling), Vision (OpenRouter)."""

from refinery.extraction.schema import (
    Bbox,
    ExtractedDocument,
    ExtractedPage,
    ExtractedTable,
    ExtractedFigure,
    TextBlock,
    FontInfo,
)
from refinery.extraction.base import Extractor, load_extraction_rules
from refinery.extraction.fast_text import FastTextExtractor
from refinery.extraction.layout_docling import LayoutExtractor, DoclingDocumentAdapter
from refinery.extraction.vision_openrouter import VisionExtractor
from refinery.extraction.router import run_extraction

__all__ = [
    "Bbox",
    "ExtractedDocument",
    "ExtractedPage",
    "ExtractedTable",
    "ExtractedFigure",
    "TextBlock",
    "FontInfo",
    "Extractor",
    "load_extraction_rules",
    "FastTextExtractor",
    "LayoutExtractor",
    "DoclingDocumentAdapter",
    "VisionExtractor",
    "run_extraction",
]
