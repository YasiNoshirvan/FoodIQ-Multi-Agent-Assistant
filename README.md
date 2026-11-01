# 🍎🥦 FoodIQ — Multi-Agent Food Assistant

**A small supervisor-based AI project for exploring fruit and vegetable information with specialized agents.**

Built with **Python, LangChain, and Groq**, FoodIQ demonstrates how a supervisor can delegate questions to different agents, use local knowledge, and combine their answers in a conversational interface.

---

## 🔍 Overview

FoodIQ has three agents:

- **Supervisor** — interprets the user's question and decides which specialist to call.
- **Fruit Expert** — looks up information about fruits.
- **Vegetable Expert** — looks up information about vegetables.

The two specialists use Python dictionaries covering **26 foods (13 fruits and 13 vegetables)**. If a fact is missing and Tavily is configured, they can also search the web.

## ✨ Features

- Supervisor-based multi-agent orchestration
- Routing to one or both specialists for cross-category questions
- Local fruit and vegetable knowledge bases
- Comparisons between foods
- Optional Tavily web search for information missing from the local data
- Conversation history during the current session
- Display of the specialists used for each answer
- Basic error handling and a command to clear chat history

## 🧠 Architecture

```text
User question
     |
     v
Supervisor Agent
     |
     +----> Fruit Expert ----> fruit_info() ----> Fruit dictionary
     |
     +----> Vegetable Expert -> veggie_info() -> Vegetable dictionary
     |
     +----> Optional Tavily search (via specialists)
     |
     v
Combined response + specialists used
```

## 🛠️ Tech Stack

**Python 3.12** · **LangChain** · **LangChain-Groq** · **Groq API (GPT-OSS-20B)** · **Tavily (optional)**

## 🚀 Getting Started

1. Clone the repository and open its directory.

   ```bash
   git clone https://github.com/YasiNoshirvan/FoodIQ-Multi-Agent-Assistant.git
   cd FoodIQ-Multi-Agent-Assistant
   ```

2. Install the required packages in a Python 3.12 environment.

   ```bash
   python -m pip install langchain langchain-groq python-dotenv
   ```

   To enable optional web search:

   ```bash
   python -m pip install langchain-tavily
   ```

3. Create a local `.env` file:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

   The Tavily key is optional. **Never commit your `.env` file.**

4. Run the assistant:

   ```bash
   python Multi_Agent_Project.py
   ```

## 💬 Example Questions

```text
Is a tomato a fruit or a vegetable?
Compare apples and carrots.
What are the differences between mango and pineapple?
Tell me about dragon fruit.
```

Use `clear` to reset the conversation or `exit` / `q` to quit.

## 📌 Scope & Limitations

This is an **educational multi-agent project**, not a nutrition or medical advisory service. The local database contains short descriptive facts rather than a complete nutritional dataset. Agent routing and web-search decisions are made by an LLM, so results may vary. Chat history is stored in memory only while the program runs.

---

*Developed as an extension of hands-on AI Engineering coursework.*
