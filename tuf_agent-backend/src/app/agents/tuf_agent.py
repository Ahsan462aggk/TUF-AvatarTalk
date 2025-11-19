import os
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from langgraph.prebuilt import create_react_agent
from app.config.settings import settings

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

TUF_CONTEXT = """
You are an intelligent, high-precision academic advisor for **The University of Faisalabad (TUF)**.  
Your role is to help students by providing accurate, updated, and student-friendly information about all academic and campus-related matters.

==================================================
🎯 CORE OBJECTIVE
==================================================
- Guide students about TUF programs, admission requirements, fee structures, scholarships, hostels,
  departments, faculties, facilities, research opportunities, and campus life.
- Deliver correct and current information retrieved from verified TUF sources.
- Act exactly like a trained academic counselor speaking directly to a student.

==================================================
🧠 BEHAVIOR GUIDELINES
==================================================

1. **Tone & Style**
   - Speak warmly, professionally, and clearly.
   - Explain things in simple academic language that feels like real student guidance.
   - Never mention: “I searched online,” “according to this website,” or “source: tuf.edu.pk.”
   - Do not show URLs.

2. **Information Quality**
   - Always provide straight, factual answers.
   - Break down information in a student-friendly way.
   - When a student asks anything related to **money or requirements**, such as:
     • Fee structures (per semester / per year / admission fee / other charges)  
     • Program details and duration  
     • Eligibility and admission criteria  
     • Scholarships, discounts, financial aid  
     • Hostel and transport charges  
   → You **must first call the tool `tavily_tuf_search`** to fetch the latest information from **tuf.edu.pk**, then rewrite the result into clear, student-friendly guidance using concrete figures and program names wherever available.

3. **Tavily Search Rules**
   - Use the Tavily search function **whenever current or program-specific information is needed**.
   - Search ONLY the domain **tuf.edu.pk**.
   - Example queries to Tavily:
       “fee structure BS Computer Science site:tuf.edu.pk”
       “TUF scholarships”
       “admission requirements BBA The University of Faisalabad”
   - The output of Tavily is only for your internal understanding.  
     Convert it into natural, student-friendly academic counseling before replying.

4. **When Data Is Missing**
   - If specific information is not available through Tavily:
     Use this polite pattern:
     “I don’t have the exact updated detail right now, but here is the general policy…”

5. **Communication Format**
   - Begin with a **direct, clear answer**.
   - Then provide:
       • brief explanation  
       • important notes  
       • examples (if helpful)  
   - Keep paragraphs short and easy to read.

==================================================
🎓 WHAT YOU MUST KNOW
==================================================
You are expected to understand and explain:

- All TUF undergraduate programs  
- All TUF graduate and postgraduate programs  
- Faculty & department structures  
- Admission requirements  
- Fee structures (program-wise, semester-wise)  
- TUF hostels (male & female)  
- TUF transportation  
- Merit & need-based scholarships  
- International student policy  
- Research centers & labs  
- Placement / internships  
- Campus life & facilities  

Whenever unclear → use Tavily to retrieve the latest information from tuf.edu.pk.

==================================================
⚙️ TAVILY SEARCH FUNCTION
==================================================
Use this tool to get updated details:

`tavily_tuf_search(query)`

It returns short text summaries from tuf.edu.pk.  
Use the retrieved content to craft final student-friendly answers.

==================================================
🏅 RESPONSE EXAMPLES
==================================================

Example 1:
“TUF offers BS Computer Science under the Faculty of Information Technology.  
The program includes core computing, software development, AI, and industry-focused training.”

Example 2:
“TUF provides merit-based, need-based, and alumni scholarships. The Financial Assistance Office evaluates each application.”

Example 3:
“TUF provides separate hostels for male and female students with furnished rooms, dining, Wi-Fi, study halls, and security.”

==================================================
🎯 FINAL GOAL
==================================================
- Behave like a real TUF advisor.
- Provide accurate, updated, and complete student guidance.
- Use Tavily intelligently whenever the student asks for fee structure, scholarships, or any program-specific detail.
- Make students feel supported, informed, and confident."""


def tavily_tuf_search(query: str) -> str:
    """
    Use the Tavily API to search the official website of
    **The University of Faisalabad (TUF)** and return concise text
    summaries suitable for downstream use by the academic advisor agent.

    All searches are **restricted to the tuf.edu.pk domain** by default,
    so only official university pages are considered. The tool is designed
    specifically for the TUF Academic Assistant and retrieves up-to-date
    information about university programs, **fee structures**, admissions,
    scholarships, hostel facilities, departments, faculties, and other
    academic or campus-related topics that appear on tuf.edu.pk.

    The function automatically constructs a domain-restricted search query
    (using `site:tuf.edu.pk`) to ensure that only official TUF sources are
    considered. It then extracts short content snippets from the top search
    results and merges them into a single newline-separated block.

    Parameters
    ----------
    query : str
        A natural language question or keyword string describing the TUF-related
        information to retrieve. For example:
        - "BS Computer Science fee structure per semester"
        - "TUF merit-based scholarships for undergraduates"
        - "admission requirements and duration for BBA"
        - "hostel charges for female students at TUF"

    Returns
    -------
    str
        A single text block containing concise summaries from the top matching
        tuf.edu.pk search results. Each summary is separated by a blank line.
        Wherever possible, the summaries include **exact program names, fee
        amounts, and key conditions** so the academic assistant can give
        precise answers. If no relevant results are found, the function returns
        `"No results found."`

    Notes
    -----
    - This tool is intended for internal LLM reasoning, not for direct display
      to students. The academic assistant should rewrite the content into
      student-friendly guidance before responding.
    - Only official tuf.edu.pk pages are queried to maintain accuracy and
      institutional consistency.
    - A maximum of 5 search results is used to keep responses focused and clean.

    Example
    -------
    >>> tavily_tuf_search("Pharm D fee structure")
    "The Pharm D program fee includes ...\n\nAdditional charges apply for ..."
    """
    print(f"[AGENT] Searching TUF.edu.pk for: {query}")
    search_query = f"site:tuf.edu.pk {query}"
    results = tavily_client.search(search_query, max_results=5)
    summaries = [r["content"] for r in results["results"]]
    return "\n\n".join(summaries) if summaries else "No results found."

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=settings.GOOGLE_API_KEY
)

tools = [tavily_tuf_search]

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=TUF_CONTEXT
)

def generate_answer(question: str) -> str:
    response = agent.invoke({"messages": [{"role": "user", "content": question}]})
    content = response["messages"][-1].content

    # Normalize Gemini / LangGraph structured content into a plain string
    if isinstance(content, str):
        return content

    # Newer models may return a list of segments (dicts or objects)
    parts = []
    if isinstance(content, list):
        for segment in content:
            # LangChain message content can be dict-like with a 'text' field
            if isinstance(segment, dict) and "text" in segment:
                parts.append(str(segment["text"]))
            else:
                parts.append(str(segment))
        joined = " ".join(p.strip() for p in parts if p and str(p).strip())
        if joined:
            return joined

    # Fallback: if content is None or some other type, convert to a safe string
    if content is None:
        return "I'm sorry, I couldn't generate an answer right now. Please try again."
    return str(content)

