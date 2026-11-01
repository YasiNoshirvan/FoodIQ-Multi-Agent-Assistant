
import os
import dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage

dotenv.load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise SystemExit("Missing GROQ_API_KEY. Add it to your existing .env file.")


# Food databases
fruits = {
    "tomato": "Botanically a fruit, but commonly used as a vegetable in cooking.",
    "apple": "A pome fruit related to roses. Contains fiber and vitamin C.",
    "banana": "A tropical fruit known for potassium and carbohydrates.",
    "orange": "A citrus fruit rich in vitamin C.",
    "strawberry": "An accessory fruit containing vitamin C and antioxidants.",
    "grape": "A small fruit that grows in clusters and contains antioxidants.",
    "mango": "A tropical stone fruit containing vitamins A and C.",
    "pineapple": "A tropical fruit containing vitamin C and bromelain.",
    "watermelon": "A fruit with high water content and lycopene.",
    "peach": "A stone fruit containing fiber and vitamin C.",
    "pear": "A sweet fruit containing dietary fiber.",
    "kiwi": "A small fruit rich in vitamin C and fiber.",
    "lemon": "A sour citrus fruit commonly used for juice and flavoring."
}

vegetables = {
    "carrot": "A root vegetable containing beta-carotene, a source of vitamin A.",
    "potato": "A starchy tuber containing carbohydrates and potassium.",
    "broccoli": "A cruciferous vegetable containing fiber and vitamin C.",
    "spinach": "A leafy green vegetable containing iron, folate and vitamin K.",
    "lettuce": "A leafy vegetable commonly used in salads.",
    "onion": "A bulb vegetable used for flavoring many dishes.",
    "garlic": "A bulb vegetable known for its strong flavor.",
    "cabbage": "A leafy cruciferous vegetable containing fiber and vitamin C.",
    "cauliflower": "A cruciferous vegetable related to broccoli.",
    "celery": "A crunchy vegetable with high water content.",
    "radish": "A root vegetable with a peppery taste.",
    "beetroot": "A root vegetable containing folate and natural pigments.",
    "asparagus": "A vegetable containing folate and vitamin K."
}


def normalize_name(name: str, database: dict) -> str: # Handle singular and plural food names
    name = name.strip().lower().strip(".,!? ")
    for prefix in ("the ", "an ", "a "):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break

    for singular in database:
        if singular.endswith("y"):
            plural = singular[:-1] + "ies"
        elif singular.endswith(("o", "ch", "sh")):
            plural = singular + "es"
        else:
            plural = singular + "s"
        if name in (singular, plural):
            return singular
    return name



def lookup_foods(names: list[str], database: dict) -> str: # Find foods in the local database
    if not names:
        return "NOT_FOUND: No food names were provided."
    results = []
    for original_name in names:
        name = normalize_name(original_name, database)

        if name in database:
            results.append(f"{name.title()}: {database[name]}")
        else:
            results.append(f"NOT_FOUND: '{original_name}' is not in the local database.")
    return "\n".join(results)



# Tools for the specialist agents
def fruit_info(fruit_names: list[str]) -> str:  
    '''Look up fruits by name. Pass separate names, e.g. ['apple', 'banana']'''
    return lookup_foods(fruit_names, fruits)
def veggie_info(veggie_names: list[str]) -> str:
    '''Look up vegetables by name. Pass separate names, e.g. ['carrot', 'potato']'''
    return lookup_foods(veggie_names, vegetables)


# Optional web search for unknown food facts
web_client = None

if os.getenv("TAVILY_API_KEY"):
    try:
        from langchain_tavily import TavilySearch
        web_client = TavilySearch(max_results=2, search_depth="basic")

    except (ImportError, ValueError) as error:
        print(f"Web search disabled: {error}")


def search_food_web(query: str) -> str:
    '''Search online for fruit or vegetable facts missing from the local database.'''
    if web_client is None:
        return "WEB_SEARCH_UNAVAILABLE: Tavily is not configured."

    try:
        data = web_client.invoke({"query": query})
        results = data.get("results", []) if isinstance(data, dict) else []
        if not results:
            return "NOT_FOUND: No useful web results were returned."
        return "\n\n".join(f"Source: {item.get('url', 'unknown')}\n"f"Information: {item.get('content', '')[:500]}" for item in results)

    except Exception as error:
        return f"WEB_SEARCH_FAILED: {type(error).__name__}"


# Configure the LLM and tools
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2)
fruit_tools = [fruit_info]
veggie_tools = [veggie_info]

if web_client is not None:
    fruit_tools.append(search_food_web)
    veggie_tools.append(search_food_web)


fruit_agent = create_agent(        # Fruit specialist agent
    model=llm, tools=fruit_tools, system_prompt=(
        "You are a fruit expert. Always use fruit_info first, passing ONE name "
        "per item in fruit_names (for example ['apple', 'banana']). "
        "Use only facts returned by tools, not your own memory. "
        "For missing foods or facts, use search_food_web if available. "
        "If web search is unavailable, say the information is not in your database. "
        "When you use web results, include their source URL. "
        "Do not invent nutrient values or facts. Keep answers short.")
)


veggie_agent = create_agent( # Vegetable specialist agent
    model=llm ,tools=veggie_tools,
    system_prompt=(
        "You are a vegetable expert. Always use veggie_info first, passing ONE name "
        "per item in veggie_names (for example ['carrot', 'potato']). "
        "Use only facts returned by tools, not your own memory. "
        "For missing vegetables or facts, use search_food_web if available. "
        "If web search is unavailable, say the information is not in your database. "
        "When you use web results, include their source URL. "
        "Do not invent nutrient values or facts. Keep answers short."
    )
)


# Tools used by the supervisor
def ask_fruit_expert(question: str) -> str:
    '''Delegate questions about fruits and comparisons involving fruits.'''
    result = fruit_agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content


def ask_veggie_expert(question: str) -> str:
    '''Delegate questions about vegetables and comparisons involving vegetables.'''
    result = veggie_agent.invoke({
        "messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content


supervisor = create_agent(   # Main supervisor agent
    model=llm, tools=[ask_fruit_expert, ask_veggie_expert],system_prompt=(
        "You are FoodIQ, a supervisor of two specialists. "
        "Always delegate questions about fruits to ask_fruit_expert, "
        "and questions about vegetables to ask_veggie_expert. "
        "For questions involving BOTH categories, call BOTH experts. "
        "For comparisons within one category, call only that expert. "
        "Known fruits: " + ", ".join(fruits) + ". "
        "Known vegetables: " + ", ".join(vegetables) + ". "
        "Tomato is a fruit for this project. "
        "Use the conversation history to resolve follow-up questions, "
        "and send specialists self-contained questions with explicit food names. "
        "For unfamiliar foods, use the relevant expert when the category is clear. "
        "Do not guess facts that specialists did not provide. "
        "If information is unavailable, explain the limitation. "
        "If asked about other types of food, explain the current fruit-and-vegetable scope. "
        "Combine specialist results into a clear, concise final answer.")
)

class FoodIQ: # Interactive chatbot with conversation memory
    def __init__(self):
        self.messages = []

    def ask(self, question: str):
        previous_count = len(self.messages)
        input_messages = self.messages + [{"role": "user", "content": question}]
        # Keep history only after a successful request
        response = supervisor.invoke({"messages": input_messages})
        new_messages = response["messages"][previous_count + 1:]
        self.messages = response["messages"]
           # Track the specialists called during this turn
        used_experts = {
            message.name
            for message in new_messages
            if isinstance(message, ToolMessage)
            and message.name in {"ask_fruit_expert", "ask_veggie_expert"}}
        return response["messages"][-1].content, used_experts


def main():
    bot = FoodIQ()
    print("FoodIQ - Multi-Agent Food Assistant")
    print("Ask about fruits and vegetables.")
    print("Type 'clear' to reset or 'exit' to quit.")
    print("Web search:", "enabled" if web_client else "disabled (local data only)")

    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "q"}:
            print("Goodbye!")
            break
        if question.lower() == "clear":
            bot.messages.clear()
            print("Conversation cleared.")
            continue

        if not question:
            continue

        try:
            answer, used = bot.ask(question)
            print("\nFoodIQ:", answer)
            experts = []
            if "ask_fruit_expert" in used:
                experts.append("Fruit Expert")

            if "ask_veggie_expert" in used:
                experts.append("Vegetable Expert")



            print("Experts used:", ", ".join(experts) if experts else "None")

        except Exception as error:
            print(f"Error ({type(error).__name__}): {error}")
            print("Check the API key, internet connection, and Groq rate limits.")


if __name__ == "__main__":
    main()
