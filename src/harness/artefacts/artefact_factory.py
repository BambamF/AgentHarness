from typing import Dict, List, Any
from .artefact import Artefact
import logging

class ArtefactFactory:

    def builder(self, artefact_type: type(Artefact), params: Dict[str, Any]) -> Artefact:
        full_params = {"artefact_id": uuid.uuid4(),
                       "execution_id": params.get("execution_id", None),
                       "producer": params.get("producer", None),
                       "timestamp": datetime.now(),
                       "confidence": 1.0,
                       "metadata": None,
                       "payload": params.get("payload", None)}
        new_artefact = artefact_type(**full_params)
        ArtefactStore.add(new_artefact)
        logging.info(f"[ARTEFACT FACTORY] Artefact Created: {type(new_artefact)} | Producer: {full_params.get("producer", None)} | Execution ID: {full_params.get("execution_id", None)} | Artefact ID: {full_params.get("artefact_id", None)} | Confidence: 1.0")
        return new_artefact
