from harness.harness import Harness
import os
import logging
from planner.planner import Planner
from permissions.permissions import PermissionManager
from memory.memory import MemoryManager
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.artefact_factory import ArtefactFactory
from harness.artefacts.repository.repository import RepositoryArtefact
from harness.artefacts.memory import MemoryArtefact
from harness.artefacts.prompt import PromptArtefact
from harness.artefacts.plan import PlanArtefact
from typing import List, Dict, Any
from anthropic import Anthropic
import html
import hashlib
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
print("api key in env ? ", "ANTHROPIC_API_KEY" in os.environ)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("Missing api key in environment, check .env key name and location")
ANTHROPIC_API_KEY = ANTHROPIC_API_KEY.strip()
MODEL_ID="claude-opus-5"

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_PATH, 'src/logging')
LOG_PATH = os.path.join(LOG_DIR, 'harness.log')

client = Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL=MODEL_ID
memory_path = os.path.join(ROOT_PATH, 'src/memory/memory.md')
agent = client
config_path = os.path.join(ROOT_PATH, 'configs/config.json')
charter_path = os.path.join(ROOT_PATH,'src/agents/charter.md')

def agent_loop(messages: List[Dict[str, Any]], artefact_store: ArtefactStore, permission_manager: PermissionManager, memory_manager: MemoryManager):
    while True:
        execution_id = uuid.uuid7()
        last_message = messages[-1].get('content')
        role = messages[-1].get('role')
        h = hashlib.sha256()
        h.update(last_message.encode('utf-8'))
        params = {
                  "caller": role,
                  "original_prompt": last_message,
                  "sanitised_prompt": html.escape(last_message),
                  "source": role,
                  "prompt_hash": h.hexdigest()}
        
        full_params = {"artefact_id": uuid.uuid4(),
                       "execution_id": execution_id,
                       "producer": role,
                       "timestamp": datetime.now(),
                       "metadata": None,
                       "payload": html.escape(last_message)}
        full_params.update(params)

        prompt_artefact = ArtefactFactory.builder(artefact_type=PromptArtefact, params=full_params, artefact_store=artefact_store, execution_id=execution_id, caller="user")
        harness = Harness(agent, MODEL, memory_path, memory_manager, config_path, charter_path, ROOT_PATH, messages, prompt_artefact, permission_manager, artefact_store, execution_id)
        print("\n\033[36m> Thinking...\033[0m")
        harness.run()
        response_artefact = artefact_store.latest_any()
        if type(response_artefact) != PlanArtefact: # Change to TerminationArtefact after dryrun
            print("Artefact type mismatch")
            logging.error(f"[AGENT LOOP] Expected artefact: PlanArtefact | Latest Artefact: {type(response_artefact)} | Prompt: {full_params.get('payload')}")
        else:
            print("\n\033[32mFinal Answer: Done plan created, check log file\033[0m")
            logging.info(f"[AGENT LOOP] Plan Artefact: {response_artefact.artefact_id} | Prompt: {full_params.get('payload')} | State: PLANNING ")
        break


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    permission_manager = PermissionManager()
    artefact_store = ArtefactStore()
    memory_manager = MemoryManager(memory_path=memory_path, artefact_store=artefact_store)
    history: List[Dict[str, Any]] = []
    while True:
        try:
            # prompt the user for a query with a coloured prompt
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history, artefact_store, permission_manager, memory_manager)
        break

if __name__ == "__main__":
    logging.basicConfig(
            filename=LOG_PATH,
            level=logging.INFO,
            format="%(asctime)s | %(message)s"
            )
    
    with open(LOG_PATH, 'a', encoding='utf-8', newline="") as log_file:
        main()
