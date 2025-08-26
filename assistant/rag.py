# import json
# from time import time
# from openai import OpenAI
# import ingest


# client = OpenAI()
# index = ingest.load_index()


# def search(query):
#     boost = {'intent': 5.817706817984619,
#               'category': 1.4272772830071567,
#               'question': 1.4070446215685373,
#               'response': 4.275690308354979}

#     results = index.search(
#         query=query,
#         filter_dict={'category': 'id'},
#         boost_dict=boost,
#         num_results=5
#     )

#     return results


# def build_prompt(query, search_results):
#     prompt_template = """
#    You are a customer support assistant for the insurance claims. 
#    Answer the following question based on the information provided in the CONTEXT from our knowledge base. 
#
#    Use only the facts from the CONTEXT to respond accurately.
#
#    QUESTION: {instruction}
#
#    CONTEXT:
#    {context}
#    """.strip()


#     context = ""
    
#     for doc in search_results:
#         context = context + f"intent: {doc['intent']}\nquestion: {doc['question']}\nanswer: {doc['response']}\n\n"
    
#     prompt = prompt_template.format(question=query, context=context).strip()
#     return prompt



# def llm(prompt):
#     response = client.chat.completions.create(
#         model="openai/gpt-oss-120b:fireworks-ai", messages=[{"role": "user", "content": prompt}]
#     )

#     answer = response.choices[0].message.content

#     token_stats = {
#         "prompt_tokens": response.usage.prompt_tokens,
#         "completion_tokens": response.usage.completion_tokens,
#         "total_tokens": response.usage.total_tokens,
#     }

#     return answer, token_stats


# evaluation_prompt_template = """
#You are an expert evaluator for a RAG system.
#Your task is to analyze the relevance of the generated answer to the given question.
#Based on the relevance of the generated answer, you will classify it
#as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

#Here is the data for evaluation:

#Question: {question}
#Generated Answer: {answer_llm}

#Please analyze the content and context of the generated answer in relation to the question
#and provide your evaluation in parsable JSON without using code blocks:

#{{
#  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
#  "Explanation": "[Provide a brief explanation for your evaluation]"
#}}
#""".strip()
#


# def evaluate_relevance(question, answer):
#     prompt = evaluation_prompt_template.format(question=question, answer=answer)
#     evaluation, tokens = llm(prompt) #, model="gpt-4o-mini")

#     try:
#         json_eval = json.loads(evaluation)
#         return json_eval, tokens
#     except json.JSONDecodeError:
#         result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
#         return result, tokens


# def rag(query):

#     t0 = time()

#     search_results = search(query)
#     prompt = build_prompt(query, search_results)
#     answer, token_stats = llm(prompt)

#     relevance, rel_token_stats = evaluate_relevance(query, answer)

#     t1 = time()
#     took = t1 - t0

#     answer_data = {
#         "answer": answer,
#         "model_used": "gpt-oss-120b",
#         "response_time": took,
#         "relevance": relevance.get("Relevance", "UNKNOWN"),
#         "relevance_explanation": relevance.get(
#             "Explanation", "Failed to parse evaluation"
#         ),
#         "prompt_tokens": token_stats["prompt_tokens"],
#         "completion_tokens": token_stats["completion_tokens"],
#         "total_tokens": token_stats["total_tokens"],
#         "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
#         "eval_completion_tokens": rel_token_stats["completion_tokens"],
#         "eval_total_tokens": rel_token_stats["total_tokens"],
#     }

#     return answer_data

import json
from time import time
from openai import OpenAI
import ingest


# Initialize OpenAI client (uses OPENAI_API_KEY from env)
client = OpenAI()

# Load index once
index = ingest.load_index()


def search(query: str):
    """Perform semantic + keyword search on the index."""
    boost = {
        "intent": 5.817706817984619,
        "category": 1.4272772830071567,
        "question": 1.4070446215685373,
        "response": 4.275690308354979,
    }

    results = index.search(
        query=query,
        filter_dict={"category": "id"},
        boost_dict=boost,
        num_results=5,
    )

    return results


def build_prompt(query: str, search_results: list[dict]) -> str:
    """Builds prompt for LLM using retrieved documents."""

    prompt_template = """
You are a customer support assistant for the insurance claims. 
Answer the following question based on the information provided in the CONTEXT from our knowledge base. 

Use only the facts from the CONTEXT to respond accurately.

QUESTION: {question}

CONTEXT:
{context}
    """.strip()

    context = ""
    for doc in search_results:
        context += (
            f"intent: {doc['intent']}\n"
            f"question: {doc['question']}\n"
            f"answer: {doc['response']}\n\n"
        )

    return prompt_template.format(question=query, context=context).strip()


def llm(prompt: str):
    """Call LLM and return answer + token stats."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:fireworks-ai",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats


evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer_llm}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()


def evaluate_relevance(question: str, answer: str):
    """Ask LLM to evaluate the relevance of its own answer."""
    prompt = evaluation_prompt_template.format(question=question, answer_llm=answer)
    evaluation, tokens = llm(prompt)

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        return {
            "Relevance": "UNKNOWN",
            "Explanation": "Failed to parse evaluation"
        }, tokens


def rag(query: str) -> dict:
    """End-to-end RAG pipeline: retrieve, generate, evaluate."""
    t0 = time()

    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt)

    relevance, rel_token_stats = evaluate_relevance(query, answer)

    took = time() - t0

    return {
        "answer": answer,
        "model_used": "gpt-oss-120b",
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "Failed to parse evaluation"
        ),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
    }

