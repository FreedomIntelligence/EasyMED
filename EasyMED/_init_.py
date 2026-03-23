"""EasyMED – core modules."""

from .consultation      import VirtualPatient
from .intent_recognition import IntentRecognizer
from .evaluation        import ClinicalEvaluator

__all__ = ["VirtualPatient", "IntentRecognizer", "ClinicalEvaluator"]
