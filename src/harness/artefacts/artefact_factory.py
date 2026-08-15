from typing import Dict, List, Any
from .artefact import Artefact
import logging
from datetime import datetime
import uuid
from uuid import UUID
from .artefact_store import ArtefactStore

class ArtefactFactory:
    @staticmethod
    def builder(artefact_type: type(Artefact), params: Dict[str, Any], artefact_store: ArtefactStore, execution_id: UUID, caller: str) -> Artefact:

        full_params = {}

        if not params.get("artefact_id"):
            full_params["artefact_id"] = uuid.uuid4()

        full_params["execution_id"] = execution_id
        full_params["producer"] = caller

        if not params.get("timestamp"):
            full_params["timestamp"] = datetime.now()

        full_params["metadata"] = None

        if not params.get("payload"):
            full_params["payload"] = None

        full_params["caller"] = caller

        full_params.update(params)

        new_artefact = artefact_type(**full_params)
        artefact_store.add(candidate=new_artefact)
        logging.info(f"[ARTEFACT FACTORY] Artefact Created: {type(new_artefact)} | Producer: {full_params.get('producer')} | Execution ID: {full_params.get('execution_id')} | Artefact ID: {full_params.get('artefact_id')}")
        return new_artefact
