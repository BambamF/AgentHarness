from typing import Dict, List, Any
from .artefact import Artefact
import logging
from datetime import datetime
import uuid
from .artefact_store import ArtefactStore

class ArtefactFactory:
    @staticmethod
    def builder(artefact_type: type(Artefact), params: Dict[str, Any], artefact_store: ArtefactStore) -> Artefact:
        new_artefact = artefact_type(**params)
        artefact_store.add(candidate=new_artefact)
        logging.info(f"[ARTEFACT FACTORY] Artefact Created: {type(new_artefact)} | Producer: {params.get('producer')} | Execution ID: {params.get('execution_id')} | Artefact ID: {params.get('artefact_id')} | Confidence: {params.get('confidence')}")
        return new_artefact
