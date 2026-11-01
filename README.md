# 🍎🥦 FoodIQ — Multi-Agent Food Assistant

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-Multi--Agent-1C3C3C) ![Groq](https://img.shields.io/badge/LLM-Groq-F55036) ![Type](https://img.shields.io/badge/Type-Educational%20Project-informational)

A small **supervisor-based multi-agent assistant** for questions about fruits and vegetables. A main agent decides whether to consult a fruit specialist, a vegetable specialist, or both, then combines their findings into a concise answer.

The project extends a basic AI Engineering course exercise with a larger local food dictionary, conversation memory, and optional web search.

## 🔍 What it does

- Uses a **Supervisor Agent** to route questions to specialized agents.
- Looks up facts about **13 fruits and 13 vegetables** stored in Python dictionaries.
- Handles simple questions, same-category comparisons, and fruit-versus-vegetable comparisons.
- Supports follow-up questions using **in-session conversation history**.
- Optionally searches the web through **Tavily** when information is missing.
- Displays which specialists contributed to a response.
- Allows users to reset the conversation with `clear`.

## 🧠 Agent workflow

```text
                        User question
                             |
                             v
                      Supervisor Agent
                       /           \
                      v             v
                Fruit Expert   Vegetable Expert
                      |             |
                Fruit dictionary  Vegetable dictionary
                       \           /
                        Optional Tavily search
                             |
                             v
                     Combined final answer
```

The supervisor may call **one or both specialists**. Tool selection is LLM-driven, so routing is not guaranteed to be identical on every run.

## 📂 Project files

```text
├── Multi_Agent_Project.py   # Main application, agents, tools, and food data
├── Pipfile
└── Pipfile.lock
```

The application runs in the terminal; no external database or frontend is required.

## ⚙️ Run locally

```bash
git clone https://github.com/YasiNoshirvan/FoodIQ-Multi-Agent-Assistant.git
cd FoodIQ-Multi-Agent-Assistant
python -m pip install langchain langchain-groq python-dotenv
```

Use **Python 3.12**. For optional Tavily search, also install:

```bash
python -m pip install langchain-tavily
```

Create a local `.env` file (do not commit it):

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

`TAVILY_API_KEY` is optional; without it the application uses only the local dictionaries.

```bash
python Multi_Agent_Project.py
```

> **Environment note:** The uploaded `Pipfile` is from an older Python 3.9 course environment and does not list the current LangChain agent dependencies. Use the installation commands above in a Python 3.12 environment.

## 💬 Try these questions

```text
Is a tomato a fruit or a vegetable?
Compare apples and carrots.
What are the differences between bananas and mangoes?
Tell me about dragon fruit.
```

Type `clear` to reset chat history and `exit` or `q` to quit.

---

*An educational project exploring LangChain tool calling, specialist agents, and supervisor-based orchestration.*
