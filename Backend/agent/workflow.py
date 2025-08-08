import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.llms import Replicate
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from models import (
    AgentState,
    ColumnsStructuredOutput,
    MainAgentStructuredOutput,
)
from prompts import AgentPrompts
from tools import Tools
from utils.data_format import data_context_format

load_dotenv()


class Agent:
    def __init__(self):
        self.replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")
        self.llm_for_reasoning = ChatOpenAI(model="gpt-4o")
        self.llm_for_explanation = ChatOpenAI(model="gpt-3.5-turbo")
        self.llm_for_classification = Replicate(
            model="ibm-granite/granite-3.2-8b-instruct",
            replicate_api_token=self.replicate_api_token,
        )
        self.memory = MemorySaver()
        self.prompts = AgentPrompts()
        self.tools = Tools()
        self.build = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(AgentState)
        graph.add_node("main_agent", self._main_agent)
        graph.add_node("agent_analysis", self._agent_analysis_data)
        graph.add_node("get_data", ToolNode(tools=[self.tools.get_data]))
        graph.add_node("save_tool_message", self._save_tool_message)
        graph.add_node("agent_data_desc", self._agent_data_description)
        graph.add_node("analysis_data", self._agent_analysis)
        graph.add_node("agent_insight", self._agent_data_insight)
        graph.add_node("agent_classification", self._agent_classification)

        graph.add_edge(START, "main_agent")
        graph.add_conditional_edges(
            "main_agent", self._main_agent_router, {"yes": END, "no": "agent_analysis"}
        )
        graph.add_conditional_edges(
            "agent_analysis",
            self._should_continue,
            {"tool_call": "get_data", "end": END},
        )
        graph.add_edge("get_data", "save_tool_message")
        graph.add_edge("save_tool_message", "agent_data_desc")
        graph.add_edge("agent_data_desc", "analysis_data")
        graph.add_edge("analysis_data", "agent_insight")
        graph.add_edge("agent_insight", "agent_classification")
        graph.add_edge("agent_classification", END)

        return graph.compile(checkpointer=self.memory)

    def _main_agent(self, state: AgentState) -> Dict[str, Any]:
        if state.is_analyis:
            return {"can_answer": False}
        agentPrompts = self.prompts.main_agent()
        llm = self.llm_for_explanation.with_structured_output(MainAgentStructuredOutput)
        human = HumanMessage(content=state.user_query)
        response = llm.invoke(agentPrompts + state.messages + [human])
        print(f"===============MAIN AGENT=============\n{response.the_answer}")
        return {
            "can_answer": response.can_answer,
            "the_answer": response.the_answer,
            "messages": state.messages
            + [human]
            + [AIMessage(content=response.the_answer)],
        }

    def _main_agent_router(self, state: AgentState) -> str:
        can_answer = state.can_answer
        if can_answer:
            return "yes"
        return "no"

    def _agent_analysis_data(self, state: AgentState) -> Dict[str, Any]:
        prompt = self.prompts.agent_analyst_data(state.is_analyis, state)
        llm = self.llm_for_reasoning.bind_tools([self.tools.get_data])
        human = HumanMessage(content=(state.user_query))
        response = llm.invoke(prompt + state.messages + [human])
        print(f"""
        ==============================PROMPT==========================
        {prompt}

        ==============================RESPONSE========================
        {response.content}
""")
        return {"messages": state.messages + [human] + [response]}

    def _should_continue(self, state: AgentState):
        last_message = state.messages[-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tool_call"
        return "end"

    def _save_tool_message(self, state: AgentState) -> Dict[str, Any]:
        last_message = state.messages[-1]
        if isinstance(last_message, ToolMessage):
            return {"data": last_message.content}
        return {"data": "Kosong"}

    def _agent_data_description(self, state: AgentState):
        prompt = self.prompts.agent_data_description(state.data)
        llm = self.llm_for_explanation.with_structured_output(ColumnsStructuredOutput)
        response = llm.invoke(prompt)
        print(f"===============AGENT DATA DESC=============\n{response}")
        return {
            "data_description": response.data_description,
            "column_description": response.columns,
        }

    def _agent_analysis(self, state: AgentState):
        analysisMean = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Kamu adalah seorang data analisis profesional yang memiliki pengalaman dalam menganalisis data.\nTugas kamu adalah membantu pengguna untuk menganalisis data yang telah mereka diberikan.\nUntuk output cukup berupa deskripsi dari data tersebut, kamu tidak perlu memberikan pertanyaan tambahan kepada pengguna.",
                ),
                (
                    "human",
                    "Tolong analisis data tersebut dengan benar. Berikut adalah detail dari data:\n- Data:\n{data}\n\n-Deskripsi dari data tersebut:\n{data_description}",
                ),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        llm = self.llm_for_reasoning
        tools = [self.tools.analize_data]
        tool_calling = create_tool_calling_agent(
            llm=llm, tools=tools, prompt=analysisMean
        )
        executor_tool = AgentExecutor(agent=tool_calling, tools=tools, verbose=True)
        result = executor_tool.invoke(
            {"data": state.data, "data_description": state.data_description}
        )
        print(f"===============AGENT ANALYSIS=============\n{result}")
        return {"data_stats": result["output"], "is_analyis": True}

    def _agent_data_insight(self, state: AgentState):
        prompt = self.prompts.agent_insight_data(
            state.data, state.data_description, state.data_stats
        )
        llm = self.llm_for_explanation
        response = llm.invoke(prompt)
        print(f"===============INSIGHT=============\n{response.content}")
        return {"insight": response.content}

    def _agent_classification(self, state: AgentState):
        prompt = self.prompts.agent_classification(state.data)
        llm = self.llm_for_classification
        response = llm.invoke(prompt)
        print(f"===============AGENT CLASSIFICATION=============\n{response}")
        return {"data_classification": response}

    def run(self, state: AgentState, thread_id: str):
        return self.build.invoke(
            state, config={"configurable": {"thread_id": thread_id}}
        )


if __name__ == "__main__":
    wf = Agent()
    thread = "thread_123"
    while True:
        user_input = input("Human: ")
        if user_input == "exit":
            break
        result1 = wf.run({"user_query": user_input}, thread)

    print(result1)
