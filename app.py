
import gradio as gr
import pandas as pd
import json
from io import BytesIO
import requests
import re
from openpyxl import Workbook

# The `sanitize_value` function is used to convert complex data types to a string and remove
# any illegal characters that Excel does not accept.
def sanitize_value(val):
    """
    Convert complex types to a string and remove illegal characters 
    that Excel does not accept.
    
    Args:
        val (object): The input value to be sanitized.
    
    Returns:
        str: The sanitized value.
    """
    if isinstance(val, bytes):
        try:
            s = val.decode("utf-8", errors="replace")
        except Exception:
            s = str(val)
        # Remove control characters (except newline and tab if desired)
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', s)
    elif isinstance(val, str):
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', val)
    elif isinstance(val, (dict, list)):
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', str(val))
    else:
        return val

# The `dataset_converter` function is the main function that handles the conversion of datasets
# between different formats (CSV, Parquet, JSONL, and XLS).
def dataset_converter(input_file, conversion_type, parquet_url):
    """
    Convert datasets between different formats (CSV, Parquet, JSONL, and XLS).
    
    Args:
        input_file (Union[bytes, str]): The input file to be converted, either as a file-like object or a file path.
        conversion_type (str): The type of conversion to perform, such as "CSV to Parquet", "Parquet to CSV", etc.
        parquet_url (str): Optional URL of a Parquet file, used for Parquet to JSONL/XLS conversion.
    
    Returns:
        Tuple[str, str]: The output file name and an informative message about the conversion.
    """
    # Initialize variables for file data and extension
    file_bytes = None
    file_name = None
    file_extension = None

    # Read the input file if provided
    if input_file is not None:
        try:
            file_bytes = input_file.read()
            file_name = input_file.name
        except AttributeError:
            file_name = input_file
            with open(file_name, "rb") as f:
                file_bytes = f.read()
        file_extension = file_name.lower().split('.')[-1]
    
    # Conversion: CSV to Parquet
    if conversion_type == "CSV to Parquet":
        if input_file is None or file_extension != "csv":
            raise ValueError("For CSV to Parquet conversion, please upload a CSV file. 📄")
        df = pd.read_csv(BytesIO(file_bytes))
        output_file = "output.parquet"
        df.to_parquet(output_file, index=False)
        converted_format = "Parquet"
        preview_str = df.head(10).to_string(index=False)
    
    # Conversion: Parquet to CSV
    elif conversion_type == "Parquet to CSV":
        if input_file is None or file_extension != "parquet":
            raise ValueError("For Parquet to CSV conversion, please upload a Parquet file. 📄")
        df = pd.read_parquet(BytesIO(file_bytes))
        output_file = "output.csv"
        df.to_csv(output_file, index=False)
        converted_format = "CSV"
        preview_str = df.head(10).to_string(index=False)
    
    # Conversion: CSV to JSONL
    elif conversion_type == "CSV to JSONL":
        if input_file is None or file_extension != "csv":
            raise ValueError("For CSV to JSONL conversion, please upload a CSV file. 📄")
        df = pd.read_csv(BytesIO(file_bytes), encoding='latin1')
        output_file = "metadata.jsonl"
        total_data = []
        for index, row in df.iterrows():
            data = {}
            file_name_val = None  # Initialize file_name for each row
            for column in df.columns:
                if column == 'file_name':
                    file_name_val = row[column]
                data[column] = row[column]
            row_data = {"file_name": file_name_val, "ground_truth": json.dumps(data)}
            total_data.append(row_data)
        with open(output_file, 'w', encoding='utf-8') as f:
            for row_data in total_data:
                f.write(json.dumps(row_data) + '\n')
        converted_format = "JSONL"
        preview_str = df.head(10).to_string(index=False)
    
    # Conversion: Parquet to JSONL
    elif conversion_type == "Parquet to JSONL":
        if input_file is not None:
            df = pd.read_parquet(BytesIO(file_bytes))
        elif parquet_url:
            response = requests.get(parquet_url)
            response.raise_for_status()
            df = pd.read_parquet(BytesIO(response.content))
            file_name = "from_url.parquet"
        else:
            raise ValueError("For Parquet to JSONL conversion, please upload a file or provide a URL. 🌐")
        
        output_file = "output.jsonl"
        def recursive_sanitize(val):
            if isinstance(val, bytes):
                return val.decode("utf-8", errors="replace")
            elif isinstance(val, dict):
                return {k: recursive_sanitize(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [recursive_sanitize(item) for item in val]
            else:
                return val

        records = df.to_dict(orient="records")
        with open(output_file, "w", encoding="utf-8") as f:
            for record in records:
                sanitized_record = recursive_sanitize(record)
                f.write(json.dumps(sanitized_record, ensure_ascii=False) + "\n")
        converted_format = "JSONL"
        preview_str = df.head(10).to_string(index=False)
    
    # Conversion: Parquet to XLS
    elif conversion_type == "Parquet to XLS":
        if input_file is not None:
            df = pd.read_parquet(BytesIO(file_bytes))
        elif parquet_url:
            response = requests.get(parquet_url)
            response.raise_for_status()
            df = pd.read_parquet(BytesIO(response.content))
            file_name = "from_url.parquet"
        else:
            raise ValueError("For Parquet to XLS conversion, please upload a file or provide a URL. 🌐")
        
        output_file = "output.xlsx"
        wb = Workbook(write_only=True)
        ws = wb.create_sheet()
        ws.append(list(df.columns))
        for row in df.itertuples(index=False, name=None):
            sanitized_row = [sanitize_value(cell) for cell in row]
            ws.append(sanitized_row)
        wb.save(output_file)
        converted_format = "XLS"
        preview_str = df.head(10).to_string(index=False)
    
    else:
        raise ValueError("Invalid conversion type selected. ⚠️")

    info_message = (
        f"Input file: {file_name if file_name is not None else 'N/A'}\n"
        f"Converted file format: {converted_format}\n\n"
        f"Preview (Top 10 Rows):\n{preview_str}\n\n"
        "Community: https://discord.gg/openfreeai 🚀"
    )
    return output_file, info_message

# The `custom_css` variable contains the custom CSS styles used to style the Gradio application.
custom_css = """
body {
    background-color: #f4f4f4;
    font-family: 'Helvetica Neue', Arial, sans-serif;
}
.gradio-container {
    max-width: 1000px;
    margin: 40px auto;
    padding: 20px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}
h1, h2 {
    color: #333333;
}
.gradio-input, .gradio-output {
    margin-bottom: 20px;
}
.gradio-button {
    background-color: #4CAF50 !important;
    color: white !important;
    border: none !important;
    padding: 10px 20px !important;
    font-size: 16px !important;
    border-radius: 6px !important;
    cursor: pointer;
}
.gradio-button:hover {
    background-color: #45a049 !important;
}
"""

# The `demo` variable represents the Gradio application that is launched.
with gr.Blocks(css=custom_css, title="Datasets Convertor") as demo:
    gr.Markdown("# Datasets Convertor 🚀")
    gr.Markdown(
        "Upload a CSV or Parquet file (or provide a Parquet file URL for Parquet to JSONL/XLS conversion) "
        "and select the conversion type. The app converts the file to the desired format and displays a preview of the top 10 rows. ✨"
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            input_file = gr.File(label="Upload CSV or Parquet File 📄")
        with gr.Column(scale=1):
            conversion_type = gr.Radio(
                choices=["CSV to Parquet", "Parquet to CSV", "CSV to JSONL", "Parquet to JSONL", "Parquet to XLS"],
                label="Conversion Type 🔄"
            )
    
    parquet_url = gr.Textbox(label="Parquet File URL (Optional) 🌐", placeholder="Enter URL if not uploading a file")
    
    convert_button = gr.Button("Convert ⚡", elem_classes=["gradio-button"])
    
    with gr.Row():
        output_file = gr.File(label="Converted File 💾")
        preview = gr.Textbox(label="Preview (Top 10 Rows) 🔍", lines=15)
    
    convert_button.click(
        fn=dataset_converter, 
        inputs=[input_file, conversion_type, parquet_url], 
        outputs=[output_file, preview]
    )
    
    gr.Markdown("**Join our Community:** [https://discord.gg/openfreeai](https://discord.gg/openfreeai) 🤝")

demo.launch()

