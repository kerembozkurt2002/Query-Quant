from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import base64
import io
import re

load_dotenv()

matplotlib.use('Agg')

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def _pick_bar_axes(df: pd.DataFrame, prompt: str) -> tuple[str | None, str]:
    """
    Decide sensible X and Y for a bar chart.
    Y: prefer 'Quantity' if present; else first numeric-like column.
    X: prefer a categorical column with >1 unique values. If none, use index numbers.
    """
    cols = list(df.columns)
    lower_map = {c.lower(): c for c in cols}

    # Pick Y
    if "quantity" in lower_map:
        y_col = lower_map["quantity"]
    else:
        # "numeric-like" means it can be coerced to numeric for at least some rows
        numeric_like = []
        for c in cols:
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().any():
                numeric_like.append(c)
        if not numeric_like:
            raise ValueError("Bar chart requires at least one numeric-like column for Y.")
        y_col = numeric_like[0]

    # Pick X (categorical / informative and not constant)
    candidate_x = [
        "Stock Symbol", "Time", "Transaction Type", "Description", "Date"
    ]
    x_col = None
    for c in candidate_x:
        if c in cols and df[c].nunique(dropna=True) > 1:
            x_col = c
            break

    return x_col, y_col


def detect_chart_type(prompt: str) -> str:
    """Detect what type of chart is requested based on the prompt."""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['pie', 'piechart', 'pie chart']):
        return 'pie'
    elif any(word in prompt_lower for word in ['bar', 'barchart', 'bar chart']):
        return 'bar'
    elif any(word in prompt_lower for word in ['line', 'linechart', 'line chart']):
        return 'line'
    elif any(word in prompt_lower for word in ['scatter', 'scatterplot', 'scatter plot']):
        return 'scatter'
    elif any(word in prompt_lower for word in ['chart', 'graph', 'plot', 'visualization']):
        return 'bar'  
    else:
        return None

def create_chart(data: pd.DataFrame, chart_type: str, title: str = None) -> str:
    """Create a chart and return it as base64 encoded string."""
    try:
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'pie':
            if len(data.columns) >= 2:
                labels = data.iloc[:, 0].tolist()
                values = data.iloc[:, 1].tolist()
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
            else:
                raise ValueError("Pie chart requires at least 2 columns")

        elif chart_type == 'bar':
            if data.empty:
                raise ValueError("No data to plot.")
            x_col, y_col = _pick_bar_axes(data, title or "")
            # Y as numeric
            y = pd.to_numeric(data[y_col], errors='coerce')
            mask = y.notna()
            y = y[mask]
            # Preserve the incoming order (your SQL already sorted by Quantity DESC)
            if x_col is not None:
                x_vals = data.loc[mask, x_col].astype(str).tolist()
                positions = range(len(y))
                plt.bar(positions, y.values)
                plt.xlabel(x_col)
                plt.xticks(positions, x_vals, rotation=45 if len(y) > 8 else 0)
            else:

                # Fall back to ordinal labels to avoid duplicate-category issues
                positions = range(len(y))
                labels = [str(i + 1) for i in positions]
                plt.bar(positions, y.values)
                plt.xlabel("Trade #")
                plt.xticks(positions, labels, rotation=0)
            plt.ylabel(y_col)



        elif chart_type == 'line':
            if len(data.columns) >= 2:
                x_col = data.columns[0]
                y_col = data.columns[1]
                plt.plot(data[x_col], data[y_col], marker='o')
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                plt.xticks(rotation=45)
            else:
                raise ValueError("Line chart requires at least 2 columns")
                
        elif chart_type == 'scatter':
            if len(data.columns) >= 2:
                x_col = data.columns[0]
                y_col = data.columns[1]
                plt.scatter(data[x_col], data[y_col])
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            else:
                raise ValueError("Scatter plot requires at least 2 columns")
        
        if title:
            plt.title(title)
        else:
            plt.title(f"{chart_type.title()} Chart")
            
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        plt.close()
        raise e

@tool
def chart_generator_agent(prompt: str, data: pd.DataFrame) -> dict:
    """
    Generates charts based on the prompt and data.
    """
    try:
        chart_type = detect_chart_type(prompt)
        
        if not chart_type:
            return {
                "status": "no_chart",
                "message": "No chart type detected in the prompt",
                "data": data.to_dict("records") if isinstance(data, pd.DataFrame) else data
            }
        
        chart_image = create_chart(data, chart_type, f"{chart_type.title()} Chart")
        
        return {
            "status": "success",
            "chart_type": chart_type,
            "chart_image": chart_image,
            "data": data.to_dict("records") if isinstance(data, pd.DataFrame) else data,
            "message": f"{chart_type.title()} chart generated successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate chart: {str(e)}",
            "data": data.to_dict("records") if isinstance(data, pd.DataFrame) else data
        } 