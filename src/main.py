from harness.harness import Harness
import os
import logging
from permissionspermission_manager import PermissionManager
from harness.artefacts.artefact_store import ArtefactStore
from harness.artefacts.prompt_artefact import PromptArtefact
from typing import List, Dict, Any
from anthropic import Anthropic
import os

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"].strip()
MODEL_ID=claude-sonnet-4-6

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT_PATH, 'log')
LOG_PATH = os.path.join(LOG_DIR, 'harness.log')

client = Anthropic(url="https://api.anthropic.com", api_key=ANTHROPIC_API_KEY)
MODEL=MODEL_ID


def agent_loop(messages: List[Dict[str, Any]], artefact_store: ArtefactStore, permission_manager: PermissionManager):
    agent = client
    memory_path = os.path.join(ROOT_PATH, 'memory/memory.md')
    config_path = os.path.join(ROOT_PATH, 'config/config.json')
    charter_path = os.path.join(ROOT_PATH,'agents/charter.md')
    planner = None
    while True:
        params = messages[-1]
        prompt_artefact = ArtefactFactory.builder(PromptArtefact, params)
        harness = Harness(agent, memory_path, config_path, charter_path, MODEL, ROOT_PATH, planner, prompt_artefact, permission_manager, artefact_store)
        print("\n\033[36m> Thinking...\033[0m")
        harness.run()
        response_artefact = artefact_store.latest_any()
        if type(response) != ReflectionArtefact:
            print("Artefact type mismatch")
            logging.error(f"[AGENT LOOP] Expected artefact: ReflectionArtefact | Latest Artefact: {type(response_artefact)} | Prompt: {params.content}")
        else:
            logging.info(f"[AGENT LOOP] Reflection Artefact: {response_artefact.content} | Prompt: {params.content}")
        break


def main():
    os.makedirs(LOG_PATH, exist_ok=True)
    permission_manager = PermissionManager()
    artefact_store = ArtefactStore()
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
        agent_loop(history, artefact_store, permission_manager)
        break

if __name__ == "__main__":
    logging.basicConfig(
            filename=LOG_PATH,
            level=logging.info,
            format="%(asctime)s | %(message)s"
            )
    with open(LOG_PATH, 'a', encoding='utf-8', newline="") as log_file:
        main()
