import logging
import ollama
from loader_retriever import MenuRetriever
import traceback
import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "60"))

ollama.base_url = "http://ollama-service:11434"  # K8s service name + port
class LLMModel:
    def __init__(self, retriever: MenuRetriever):
        self.retriever = retriever

    def generate_response(self, customer_text, call_type=None, call_target=None, history=None):
        try:
            context = self.retriever.get_relevant_chunks(customer_text, top_k=2)

            system_prompt = (
                "You're an AI assistant making a phone call for the user.\n"
                f"The call is to: {call_target or 'someone'}.\n"
                f"The reason for the call is: {call_type or 'general'}.\n\n"
                "Speak like a real person: casual for friends, professional for doctors or businesses.\n"
                "Be short, clear, and friendly.\n\n"
                "Here's relevant context (like menu info or past data):\n"
                f"{context}\n\n"
                "Generate what the AI should say word-for-word during the call."
            )

            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": customer_text}
                ],
                stream=False,
                options={
                    "num_predict": OLLAMA_NUM_PREDICT,
                    "temperature": OLLAMA_TEMPERATURE
                }
            )
            return response['message']['content']
        except Exception as e:
            logging.error(f"Ollama Error: {e}")
            logging.debug(traceback.format_exc())
            return "I'm having trouble generating right now. Please call ALI Daho."

