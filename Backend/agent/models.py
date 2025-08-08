from typing import Annotated, Any, Dict, List, Optional, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class MainAgentStructuredOutput(BaseModel):
    """"""

    can_answer: bool = Field(
        ..., description="Apakah asisten dapat menjawab pertanyaan ini?"
    )
    the_answer: str = Field(
        ..., description="Jawaban dari pertanyaan ini jika asisten dapat menjawab"
    )


class Columns(BaseModel):
    column_name: str = Field(..., description="Nama kolom dari tabel tersebut")
    column_description: str = Field(..., description="Deskripsi dari kolom tersebut")


class ColumnsStructuredOutput(BaseModel):
    """Kolom tabel"""

    columns: List[Columns] = Field(
        ..., description="List dari kolom dari tabel tersebut"
    )
    data_description: str = Field(
        ..., description="Deskripsi/penjelasan dari data tersebut tentang apa"
    )


# class ColumnDescription(BaseModel):
#     Column_name: str = Field(..., description="Nama kolom")
#     Description: str = Field(..., description="Deskripsi dari kolom tersebut")


# class ColumnDescriptionStructuredOutput(BaseModel):
#     """Deskripsi kolom tabel"""

#     column_descriptions: List[ColumnDescription] = Field(
#         ..., description="List dari deskripsi kolom dari tabel tersebut"
#     )


class DataStats1StructuredOutput(BaseModel):
    """Menghitung statistik data seperti mean, median, dan modus"""

    mean: float = Field(..., description="Rata-rata dari data")
    median: float = Field(..., description="Nilai tengah dari data")
    modus: float = Field(..., description="Nilai yang paling sering muncul dalam data")


class DataStats2StructuredOutput(BaseModel):
    """Menghitung statistik data seperti standard deviation, min, dan max"""

    standard_deviation: float = Field(..., description="Deviasi standar dari data")
    min: float = Field(..., description="Nilai minimum dari data")
    max: float = Field(..., description="Nilai maksimum dari data")


class DataStats(BaseModel):
    """Statistik data"""

    stats1: DataStats1StructuredOutput = Field(..., description="Statistik data 1")
    stats2: DataStats2StructuredOutput = Field(..., description="Statistik data 2")


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_query: str
    data: Optional[str] = None
    data_classification: Optional[str] = None
    data_description: Optional[str] = None
    column_description: Optional[list[Columns]] = None
    data_stats: Optional[str] = None
    is_analyis: bool = False
    insight: Optional[str] = None
    can_answer: Optional[bool] = None
    the_answer: Optional[str] = None
