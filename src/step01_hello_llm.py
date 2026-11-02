"""
step01_hello_llm.py
Step 1: Send one question to a local LLM (Ollama) and print the answer.

Run from the project folder with the virtual environment on:
    python src/step01_hello_llm.py
"""

import sys
import time

import ollama

# --- Settings (change these to experiment) ---
MODEL = "gemma3:1b"   # the model you downloaded with `ollama pull`
TEMPERATURE = 0.0     # 0 = predictable answers, higher = more variety
SYSTEM_PROMPT = "You are a cybersecurity assistant. Answer in one or two sentences."
QUESTION = "Which MITRE ATT&CK technique ID matches this: an attacker created a scheduled task so their malware runs again after the computer restarts? Give only the ID and name."


def ask_llm(question: str, system_prompt: str, temperature: float) -> str:
    """
    Send one question to the model and return its answer as text.

    Args:
        question: what the user is asking.
        system_prompt: standing rules for how the model should answer.
        temperature: how random the answer is (0 = most predictable).

    Returns:
        The model's answer, with extra spaces trimmed off.
    """
    # TODO 1: Build the list of messages.
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # TODO 2: Send the messages to the model.
    # Call ollama.chat(...) with three arguments:
    #   model=MODEL, messages=messages, options={"temperature": temperature}
    # Save the result in `response`.
    response = ollama.chat(model=MODEL, messages=messages, options={"temperature": temperature})

    # TODO 3: Return the answer text.
    # The text is at response.message.content
    # Add .strip() on the end to remove extra spaces and blank lines.
    return response.message.content.strip()


def main() -> int:
    """Ask the question and print the answer. Returns 0 on success, 1 on failure."""
    print(f"Asking {MODEL} (temperature={TEMPERATURE})...\n")
    start = time.perf_counter()

    try:
        answer = ask_llm(QUESTION, SYSTEM_PROMPT, TEMPERATURE)
    except ConnectionError:
        # The ollama library raises this when the Ollama app isn't running.
        print("Could not reach Ollama. Open the Ollama app and try again.")
        return 1
    except ollama.ResponseError as err:
        # Ollama answered with an error, for example the model isn't downloaded.
        print(f"Ollama returned an error: {err.error}")
        print(f"If the model is missing, run: ollama pull {MODEL}")
        return 1

    seconds = time.perf_counter() - start
    print("QUESTION:", QUESTION)
    print("ANSWER:  ", answer)
    print(f"\n(took {seconds:.1f} seconds)")
    return 0


# Runs main() only when you run this file directly.
if __name__ == "__main__":
    sys.exit(main())