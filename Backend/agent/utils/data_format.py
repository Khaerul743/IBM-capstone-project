import pandas as pd
from models import AgentState


def beauty_output(path: str):
    df = pd.read_csv(path)
    return df.to_string()


def data_context_format(state: AgentState):
    column_description = ""
    try:
        for column in state.column_description:
            column_description += (
                f"Kolom {column.column_name}: {column.column_description}"
            )
    except:
        column_description = "Kosong"

    return f"""

**Berikut adalah detail data yang dikirim oleh pengguna**
{state.data}

{state.data_description}
    
**Deskripsi kolom dari data tersebut**
{column_description}

**Hasil dari perhitungan statistik yang telah dilakukan**
{state.data_stats}

**Insight dari data**
{state.insight}
    """
