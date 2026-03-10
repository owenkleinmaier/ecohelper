import time
import requests
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import chromadb
from newspaper import Article
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vectors()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

urls = [
    "https://www.epa.gov/recycle",
    "https://www.epa.gov/energy/learn-about-energy-and-its-impact-environment",
    "https://www.epa.gov/smm/sustainable-materials-management-basics",
    "https://www.epa.gov/soakuptherain/what-you-can-do-soak-rain",
    "https://www.epa.gov/watersense",
    "https://www.epa.gov/climate-change-science",
    "https://www.epa.gov/greenpower/green-power-partnership-frequently-asked-questions",
    "https://www.epa.gov/recycle/recycling-basics",
    "https://www.epa.gov/energy/clean-energy-programs",
    "https://www.energy.gov/energysaver/energy-saver",
    "https://www.epa.gov/energy/learn-about-energy-and-its-impact-environment",
    "https://www.epa.gov/energy/reduce-environmental-impact-your-energy-use",
    "https://www.energy.gov/energysaver/lighting-choices-save-you-money",
    "https://www.epa.gov/power-sector/electric-power-sector-basics",
    "https://www.energy.gov/energysaver/air-sealing-your-home",
    "https://www.energy.gov/energysaver/home-heating-systems",
    "https://www.energy.gov/energysaver/windows-doors-and-skylights",
    "https://earth911.com/home-garden/environmentally-friendly-cleaning/",
    "https://earth911.com/home-garden/eco-friendly-cleaning-vendor-5-tips/",
    "https://earth911.com/eco-tech/energy-saving-technologies-adopt/",
    "https://earth911.com/eco-tech/how-to-save-energy-in-your-home-with-smart-plugs/",
    "https://earth911.com/home-garden/7-steps-zero-waste-lifestyle/",
    "https://earth911.com/living-well-being/simple-swaps-healthy-thanksgiving/",
    "https://earth911.com/how-to-recycle/recycling-mysteries-styrofoam/",
    "https://earth911.com/home-garden/reducing-refrigerators-co2-emissions/",
    "https://earth911.com/home-garden/beyond-beekeeping-protect-pollinators/",
    "https://earth911.com/living-well-being/green-living-tips-fall/",
    "https://earth911.com/home-garden/garage-reuse-recycling/",
    "https://earth911.com/eco-tech/dead-cell-phone-what-to-do/",
    "https://earth911.com/eco-tech/guest-idea-how-communities-can-view-real-time-satellite-images-to-respond-to-natural-disasters/",
    "https://earth911.com/business-policy/solar-farms-food-security-wildlife-habitat/",
    "https://earth911.com/how-and-buy/6-tips-for-buying-a-used-electric-vehicle/",
    "https://www.epa.gov/recycle/electronics-donation-and-recycling",
    "https://www.epa.gov/recycle/used-household-batteries",
    "https://www.epa.gov/recycle/used-lithium-ion-batteries",
    "https://www.epa.gov/recycle/preventing-wasted-food-home",
    "https://www.epa.gov/recycle/composting-home",
    "https://www.epa.gov/hw/defining-hazardous-waste-listed-characteristic-and-mixed-radiological-wastes",
    "https://www.epa.gov/international-cooperation/cleaning-electronic-waste-e-waste",
    "https://www.epa.gov/landfills/basic-information-about-landfills",
    "https://www.epa.gov/landfills/municipal-solid-waste-landfills",
    "https://www.epa.gov/landfills/bioreactor-landfills",
    "https://www.epa.gov/landfills/industrial-and-construction-and-demolition-cd-landfills",
    "https://www.epa.gov/rcra/resource-conservation-and-recovery-act-rcra-overview",
    "https://www.epa.gov/sustainable-management-food/sustainable-management-food-basics",
    "https://www.epa.gov/sustainable-management-food/wasted-food-scale",
    "https://www.epa.gov/sustainable-management-food/composting",
    "https://www.epa.gov/sustainable-management-food/food-donation-basics",
    "https://www.epa.gov/sustainable-management-food/forms/composting-food-scraps-your-community-social-marketing-toolkit",
    "https://www.epa.gov/smartgrowth/about-smart-growth",
    "https://www.epa.gov/smartgrowth/smart-growth-small-towns-and-rural-communities",
    "https://www.epa.gov/smartgrowth/smart-growth-and-housing",
    "https://www.epa.gov/smartgrowth/building-blocks-sustainable-communities",
    "https://www.epa.gov/smartgrowth/local-foods-local-places",
    "https://www.epa.gov/smartgrowth/rethinking-highways-healthy-communities",
    "https://www.epa.gov/smartgrowth/equitable-resilience-technical-assistance",
    "https://www.epa.gov/smartgrowth/location-and-green-building",
    "https://www.epa.gov/natural-disasters/hurricanes",
    "https://www.epa.gov/re-powering/what-re-powering",
    "https://www.epa.gov/mold/what-are-molds",
    "https://www.epa.gov/mold/mold-and-your-home",
    "https://www.epa.gov/ozone-layer-protection/information-ozone-and-ozone-depletion",
    "https://www.epa.gov/visibility/visibility-parks-and-wilderness-areas",
    "https://www.epa.gov/climatechange-science/basics-climate-change",
    "https://www.epa.gov/climatechange-science/causes-climate-change",
    "https://www.epa.gov/climatechange-science/impacts-climate-change",
    "https://www.epa.gov/climatechange-science/future-climate-change",
    "https://www.epa.gov/climatechange-science/extreme-heat",
    "https://www.epa.gov/climatechange-science/extreme-precipitation",
    "https://www.epa.gov/climatechange-science/frequently-asked-questions-about-climate-change",
]

store = {}
collection = None

# store memory function
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def init_vectors():
    global collection
    
    def extract_text(url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text.strip()
        except:
            return ""

    client = chromadb.PersistentClient(path="./vectors")
    collection = client.get_or_create_collection("eco_docs")

    if collection.count() == 0:
        corpus = []
        for url in urls:
            text = extract_text(url)
            if text:
                corpus.append({"url": url, "text": text})
            time.sleep(1)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=900, chunk_overlap=150,
            separators=["\n\n", "\n", ".", " "]
        )
        docs = []
        for entry in corpus:
            base = Document(page_content=entry["text"], metadata={"source": entry["url"]})
            chunks = splitter.split_documents([base])
            docs.extend(chunks)

        for i, doc in enumerate(docs):
            emb = ollama.embed(model="nomic-embed-text", input=doc.page_content)
            collection.add(
                ids=[f"doc_{i}"],
                embeddings=emb["embeddings"],
                documents=[doc.page_content],
                metadatas=[doc.metadata]
            )

    return collection

def get_relevant_context(prompt, n_results=2):
    r = ollama.embed(model="nomic-embed-text", input=prompt)
    q_emb = r["embeddings"]
    res = collection.query(query_embeddings=q_emb, n_results=n_results)
    
    context = ""
    sources = []
    if res and "documents" in res:
        context = " ".join(res["documents"][0])
        if "metadatas" in res:
            sources = [m.get("source", "") for m in res["metadatas"][0]]
    
    return context, sources

# 3 tools


# Tool 1: for chatbot to use RAG when needed
@tool
def get_sustainable_advice(question: str) -> str:
    """Search knowledge base for sustainability advice and information on recycling, energy, composting, and environmental topics.
    
    Args:
        question: The user's question about sustainability
    """
    context, sources = get_relevant_context(question, n_results=3)
    global sources_cache
    sources_cache = sources
    return context

# Tool 2: calls waqi public api to retrieve air quality for a certain city
@tool  
def get_air_quality(city: str, country: str = "US") -> dict:
    """get current air quality data for a city using waqi"""

    # build waqi url, only city is used
    url = f"https://api.waqi.info/feed/{city}/"
    r = requests.get(url, params={"token": os.getenv("WAQI_API_TOKEN")})
    data = r.json()

    d = data.get("data", {})
    iaqi = d.get("iaqi", {})

    measurements = []
    for k, v in iaqi.items():
        measurements.append(
            {
                "parameter": k,
                "value": v.get("v"),
            }
        )

    return {
        "source": "waqi",
        "city": d.get("city", {}).get("name"),
        "aqi": d.get("aqi"),
        "measurements": measurements,
    }


# Topic 3: Calls climateiq API to calculate emissions use for vechicles and flights
@tool
def get_carbon_footprint(activity_type: str, value: float, unit: str = "mi") -> dict:
    """get simple co2 estimate for driving or flying using climatiq"""

    if activity_type == "driving":
        factor_id = "8808d446-cfa5-431f-a0b1-0437624ebf2c"
    elif activity_type == "flight":
        factor_id = "5ef0304f-edea-4aa6-9730-75d5adedd2b2"
    else:
        return {"error": "use 'driving' or 'flight' for activity_type"}

    u = unit.lower()
    if u in ["mile", "miles"]:
        distance_unit = "mi"
    elif u in ["km", "kilometer", "kilometers"]:
        distance_unit = "km"
    else:
        distance_unit = "mi"

    api_key = os.getenv("CLIMATIQ_API_KEY")
    url = "https://api.climatiq.io/data/v1/estimate"

    body = {
        "emission_factor": {
            "id": factor_id
        },
        "parameters": {
            "distance": value,
            "distance_unit": distance_unit
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=body, headers=headers)
    data = r.json()

    co2e = data.get("co2e")

    return {
        "activity_type": activity_type,
        "value": value,
        "unit": distance_unit,
        "co2e_kg": co2e
    }




# start creating model and chain
def classify_style(input_dict):
    q = input_dict["question"]
    if any(w in q.lower() for w in ["define", "explain", "list", "what is", "how many", "step", "steps"]):
        style = "precise"
    else:
        style = "creative"
    return {**input_dict, "style": style}

#  (vi) varying generation parameters based on question style
def pick_llm(input_dict):
    style = input_dict["style"]
    
    if style == "precise":
        base_model = ChatOllama(
            model="huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF:latest",
            temperature=0.2, top_p=0.8, top_k=40, num_predict=400
        )
    else:
        base_model = ChatOllama(
            model="huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF:latest",
            temperature=0.6, top_p=0.9, top_k=60, num_predict=400
        )
    
    return {**input_dict, "llm": base_model, "style": style}

#  (i) task decomposition
planner_prompt = ChatPromptTemplate.from_template(
    "Plan your reasoning before answering.\n"
    "List 2–4 short steps for how you will approach this question.\n"
    "Question: {question}"
)

# (v) structured outputs and  (iii) role playing
structured_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are EcoHelper, a friendly environmental mentor helping people live sustainably."
            "you have access to the full conversation history in the `history` messages.\n"
            "you are allowed to use information from that history, including the user's name, "
            "preferences, and what you have already talked about.\n"
            "when carbon emissions data appears in the context"
            "you must use that data as the main source for your answer. explain the results so they are interpretable, maybe even put in a comparison "
            "but do not introduce different estimates from the epa or other sources, and do "
            "not change the co2e_kg value.\n"
            "if the user asks meta questions like 'what is my name?' or 'what have we talked about so far?', "
            "read the history messages and answer based only on what appears there.\n"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "Using this plan and memory context, write a clear, natural, and concise answer.\n"
              "If the question asks for a process or 'how-to', include short steps or bullet points.\n"
              "when air quality data appears in the context (aqi, measurements, etc.), "
              "base your answer on that data and do not invent numbers or claim you checked "
              "airnow.gov or epa.gov unless they are explicitly mentioned in the context."
              "Otherwise, write a complete and fluent answer.\n\n"
              "Plan:\n{plan}\n\nContext:\n{ctx}\n\nQuestion:\n{question}")
])

# (iv) refining feedback
refine_prompt = ChatPromptTemplate.from_template(
    "Improve the clarity and flow of this answer, but do not describe the changes. "
    "Return only the final improved version, phrased naturally for the user.\n\nAnswer:\n{answer}"
)

finalize_prompt = ChatPromptTemplate.from_template(
    "You are EcoHelper's final reviewer. Take the improved answer and make it sound perfectly natural, friendly, "
    "and helpful to a general audience. Keep it concise, accurate, and warm. "
    "Do not describe what you changed or list improvements, just return the final polished version of the answer itself"
    "Do not mention that it is a final answer or that you are the reviewer, you are still EcoHelper! and deliver as if you are delivering the entire answer directly to a user\n\n"
    "Answer:\n{answer}"
)

# functions for my chain 


sources_cache = []

def add_context(input_dict):
    global sources_cache
    ctx, sources = get_relevant_context(input_dict["question"])
    sources_cache = sources
    
    if "tool_context" in input_dict:
        ctx = input_dict["tool_context"] + "\n\n" + ctx
    
    return {**input_dict, "ctx": ctx}

def plan_step(input_dict):
    plan_llm = input_dict["llm"]
    plan = plan_llm.invoke(planner_prompt.format_messages(question=input_dict["question"])).content
    return {**input_dict, "plan": plan}

def structured_step(input_dict):
    llm = input_dict["llm"]
    history = input_dict.get("history", [])
    response = llm.invoke(structured_prompt.format_messages(
        history=history,
        plan=input_dict["plan"],
        ctx=input_dict["ctx"],
        question=input_dict["question"]
    )).content
    return {**input_dict, "raw_answer": response}

def refine_step(input_dict):
    llm = input_dict["llm"]
    refined = llm.invoke(refine_prompt.format_messages(answer=input_dict["raw_answer"])).content
    return {**input_dict, "final_answer": refined}

def finalize_step(input_dict):
    llm = input_dict["llm"]
    polished = llm.invoke(finalize_prompt.format_messages(answer=input_dict["final_answer"])).content
    return {**input_dict, "final_answer": polished, "output": polished}

def execute_tools(input_dict):
    llm = input_dict["llm"]
    question = input_dict["question"]

    tools = [get_sustainable_advice, get_air_quality, get_carbon_footprint]
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(
            content=(
                "you are a router that decides when to call tools.\n"
                "use get_air_quality for air quality questions.\n"
                "use get_carbon_footprint for driving or flying co2 questions about emissions.\n"
                "use get_sustainable_advice for general sustainability questions.\n"
                "only call tools when actual data is required."
            )
        ),
        HumanMessage(content=question),
    ]

    response = llm_with_tools.invoke(messages)

    tools_called = []
    tool_results = []

    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_map = {
            "get_sustainable_advice": get_sustainable_advice,
            "get_air_quality": get_air_quality,
            "get_carbon_footprint": get_carbon_footprint,
        }

        for tool_call in response.tool_calls:
            selected_tool = tool_map.get(tool_call["name"])
            if selected_tool:
                tools_called.append(tool_call["name"])
                result = selected_tool.invoke(tool_call)
                tool_results.append(str(result))

    if tool_results:
        input_dict["tool_context"] = " ".join(tool_results)
        input_dict["tools_used"] = tools_called

    return input_dict

# long chain of everything, each runnableLambda runs the functions and passes variables in betweenm
eco_chain = (
    RunnablePassthrough()
    | RunnableLambda(classify_style)
    | RunnableLambda(pick_llm)
    | RunnableLambda(execute_tools)
    | RunnableLambda(add_context)
    | RunnableLambda(plan_step)
    | RunnableLambda(structured_step)
    | RunnableLambda(refine_step)
    | RunnableLambda(finalize_step)
)

# adds memory to the chain
chain_with_history = RunnableWithMessageHistory(
    eco_chain,
    get_session_history=get_session_history,
    history_messages_key="history",
    input_messages_key="question"
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "session1"

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # clear sources from previous request
    global sources_cache
    sources_cache = []

    # run the rag chain with session memory
    result = chain_with_history.invoke(
        {"question": req.message},
        config={"configurable": {"session_id": req.session_id}},
    )


    return ChatResponse(
        answer=result["final_answer"],
        sources=list(set(sources_cache))
    )

@app.post("/clear")
def clear_session(session_id: str = "session1"):
    # wipe chat history for  session
    if session_id in store:
        store[session_id] = ChatMessageHistory()
    return {"status": "cleared"}
