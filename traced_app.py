"""Send three independent prompts to OpenAI through LangChain.

Set API credentials and other runtime configuration in the terminal before running.
"""

from time import perf_counter

from langchain_openai import ChatOpenAI


PROMPTS = (
    "What is a large language model? Answer in one sentence of at most 25 words.",
    "Explain how a prompt template helps a Python developer. Give three concise "
    "bullet points and one short example. Keep your answer under 120 words.",
    "Write a beginner-friendly guide to debugging a Python application that calls "
    "a language model. Cover incorrect prompts, authentication errors, rate limits, "
    "response quality, latency, and token costs. Include a concrete example for "
    "each topic and finish with a practical checklist. Aim for 500 to 600 words.",
)

from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_completion_tokens=1200,
        timeout=90,
        max_retries=2,
    )

    for number, prompt in enumerate(PROMPTS, start=1):
        print(f"\n{'=' * 72}\nRUN {number}\nPROMPT: {prompt}", flush=True)
        started = perf_counter()
        response = llm.invoke(prompt)
        elapsed = perf_counter() - started

        print(f"\nANSWER:\n{response.content}")
        print(f"\nLocal elapsed time: {elapsed:.2f} seconds")
        usage = response.usage_metadata or {}
        print(
            f"Tokens - input: {usage.get('input_tokens', 'unavailable')}, "
            f"output: {usage.get('output_tokens', 'unavailable')}, "
            f"total: {usage.get('total_tokens', 'unavailable')}"
        )


if __name__ == "__main__":
    main()
