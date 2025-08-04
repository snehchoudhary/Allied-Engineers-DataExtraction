
# # backend/main.py
# from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import tempfile
# import os
# from typing import List, Optional

# app = FastAPI()

# # Allow CORS for your frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://allied-engineers-dataextraction-2frontend.onrender.com"],  # change to your frontend URL in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------------------
# # Helper: Read file
# # ---------------------------
# def read_file(file_path: str) -> pd.DataFrame:
#     if file_path.endswith(('.xlsx', '.xls')):
#         return pd.read_excel(file_path)
#     elif file_path.endswith('.csv'):
#         return pd.read_csv(file_path)
#     else:
#         raise ValueError("Unsupported file format")

# # ---------------------------
# # AC Interference
# # ---------------------------
# def ac_interference_analysis(df: pd.DataFrame) -> pd.DataFrame:
#     df.columns = df.columns.str.strip()
#     df['Comment'] = df['Comment'].fillna('').astype(str)
#     df['Normalized_Comment'] = df['Comment'].str.lower()

#     base_keywords = ['ac interference']
#     results = []
#     start_row, start_index, current_keyword = None, None, None

#     for i, row in df.iterrows():
#         comment = row['Normalized_Comment'].strip().replace(';', '').strip()

#         for keyword in base_keywords:
#             if f"{keyword} start" in comment:
#                 start_row, start_index, current_keyword = row, i, keyword
#                 break

#         if start_row is not None and f"{current_keyword} end" in comment:
#             end_row, end_index = row, i
#             attenuation_avg = df.loc[start_index:end_index, 'Attenuation'].mean()

#             result = start_row.to_dict()
#             result.update({
#                 'End VirtualDistance (m)': end_row.get('VirtualDistance (m)', ''),
#                 'End Latitude': end_row.get('Latitude', ''),
#                 'End Longitude': end_row.get('Longitude', ''),
#                 'Average Attenuation': attenuation_avg
#             })

#             if 'Station m' in df.columns:
#                 result['End Station m'] = end_row['Station m']

#             results.append(result)
#             start_row, current_keyword = None, None

#     output_df = pd.DataFrame(results)
#     output_df['Length (m)'] = output_df['End VirtualDistance (m)'] - output_df['VirtualDistance (m)']
#     return output_df

# # ---------------------------
# # ACPSP Above Threshold
# # ---------------------------
# def acpsp_analysis(df: pd.DataFrame, threshold: float = 4) -> pd.DataFrame:
#     if 'Station m' in df.columns:
#         df['GAIL End Ch. (m)'] = df['Station m']

#     df['XLI End Ch. (m)'] = df['VirtualDistance (m)']
#     df['End Latitude'] = df['Latitude']
#     df['End Longitude'] = df['Longitude']

#     df['Above_Threshold'] = df['ACPSP_OnPotential'] > threshold

#     def process_group(group):
#         if group['Above_Threshold'].any():
#             max_value = group['ACPSP_OnPotential'].max()
#             group['Highest_AC_PSP_V'] = max_value
#             if len(group) > 1:
#                 if 'GAIL End Ch. (m)' in group.columns:
#                     group.iloc[0, group.columns.get_loc('GAIL End Ch. (m)')] = group.iloc[-1]['GAIL End Ch. (m)']
#                 group.iloc[0, group.columns.get_loc('End Latitude')] = group.iloc[-1]['End Latitude']
#                 group.iloc[0, group.columns.get_loc('End Longitude')] = group.iloc[-1]['End Longitude']
#                 group.iloc[0, group.columns.get_loc('XLI End Ch. (m)')] = group.iloc[-1]['XLI End Ch. (m)']
#         return group

#     df = df.groupby((df['Above_Threshold'] != df['Above_Threshold'].shift()).cumsum(), group_keys=False).apply(process_group)
#     df = df[df['Above_Threshold']].loc[df['Above_Threshold'] != df['Above_Threshold'].shift()]
#     df = df.drop(columns=['Above_Threshold'])
#     df['Length (m)'] = df['XLI End Ch. (m)'] - df['VirtualDistance (m)']
#     return df

# # ---------------------------
# # Attenuation Above Threshold
# # ---------------------------
# def attenuation_analysis(df: pd.DataFrame, threshold: float = 2) -> pd.DataFrame:
#     df['End Latitude'] = df['Latitude']
#     df['End Longitude'] = df['Longitude']
#     df['XLI End Ch. (m)'] = df['VirtualDistance (m)']
#     df['Above_Threshold'] = df['Attenuation'] > threshold

#     def process_group(group):
#         if group['Above_Threshold'].any():
#             max_row = group.loc[group['Attenuation'].idxmax()]
#             min_row = group.loc[group['Attenuation'].idxmin()]
#             group['Average Attenuation'] = group['Attenuation'].mean()
#             group['Max Attenuation Value'] = max_row['Attenuation']
#             group['Min Attenuation Value'] = min_row['Attenuation']
#         return group

#     df = df.groupby((df['Above_Threshold'] != df['Above_Threshold'].shift()).cumsum(), group_keys=False).apply(process_group)
#     df = df[df['Above_Threshold']].loc[df['Above_Threshold'] != df['Above_Threshold'].shift()]
#     df = df.drop(columns=['Above_Threshold'])
#     df['Length (m)'] = df['XLI End Ch. (m)'] - df['VirtualDistance (m)']
#     return df

# # ---------------------------
# # CPCIPS Below Threshold
# # ---------------------------
# def cpcips_analysis(df: pd.DataFrame, threshold: float = -1.0) -> pd.DataFrame:
#     if 'Station m' in df.columns:
#         df['GAIL End Ch. (m)'] = df['Station m']

#     df['XLI End Ch. (m)'] = df['VirtualDistance (m)']
#     df['End Latitude'] = df['Latitude']
#     df['End Longitude'] = df['Longitude']
#     df['Above_Threshold'] = df['CPCIPS_OnPotential'] < threshold

#     def process_group(group):
#         if group['Above_Threshold'].any():
#             min_value = group['CPCIPS_OnPotential'].min()
#             group['Lowest_CPCIPS_OnPotential'] = min_value
#         return group

#     df = df.groupby((df['Above_Threshold'] != df['Above_Threshold'].shift()).cumsum(), group_keys=False).apply(process_group)
#     df = df[df['Above_Threshold']].loc[df['Above_Threshold'] != df['Above_Threshold'].shift()]
#     df = df.drop(columns=['Above_Threshold'])
#     df['Length (m)'] = df['XLI End Ch. (m)'] - df['VirtualDistance (m)']
#     return df

# # ---------------------------
# # Landuse
# # ---------------------------
# def landuse_analysis(df: pd.DataFrame) -> pd.DataFrame:
#     df.columns = df.columns.str.strip()
#     df['Comment'] = df['Comment'].fillna('').astype(str)
#     df['Normalized_Comment'] = df['Comment'].str.lower()
#     base_keywords = [
#         'road', 'surface pavement', 'gravel', 'surfaced pavement', 'gravel surface',
#         'surfaced - pavement', 'surfaced-pavement', 'surface-pavement', 'rocky', 
#         'cobble', 'surface - pavement', 'highway', 'railroad tracks'
#     ]
#     results = []
#     start_row, start_index, current_keyword = None, None, None

#     for i, row in df.iterrows():
#         comment = row['Normalized_Comment']
#         for keyword in base_keywords:
#             if f"{keyword} start" in comment:
#                 start_row, start_index, current_keyword = row, i, keyword
#                 break
#         if start_row is not None and f"{current_keyword} end" in comment:
#             end_row, end_index = row, i
#             attenuation_avg = df.loc[start_index:end_index, 'Attenuation'].mean()
#             result = start_row.to_dict()
#             result.update({
#                 'End Chainage (m)': end_row['VirtualDistance (m)'],
#                 'End Latitude': end_row['Latitude'],
#                 'End Longitude': end_row['Longitude'],
#                 'Average Attenuation': attenuation_avg
#             })
#             results.append(result)
#             start_row, current_keyword = None, None

#     output_df = pd.DataFrame(results)
#     output_df['Length (m)'] = output_df['End Chainage (m)'] - output_df['VirtualDistance (m)']
#     return output_df

# # ---------------------------
# # Process Pipeline
# # ---------------------------
# # def process_pipeline(file_path: str, selections: List[str], thresholds: dict) -> dict:
# #     df = read_file(file_path)
# #     results = {}
# #     if "AC Interference" in selections:
# #         results["AC Interference"] = ac_interference_analysis(df.copy())
# #     if "ACPSP" in selections:
# #         results["ACPSP"] = acpsp_analysis(df.copy(), thresholds.get("ACPSP", 4))
# #     if "Attenuation" in selections:
# #         results["Attenuation"] = attenuation_analysis(df.copy(), thresholds.get("Attenuation", 2))
# #     if "CPCIPS" in selections:
# #         results["CPCIPS"] = cpcips_analysis(df.copy(), thresholds.get("CPCIPS", -1.0))
# #     if "Landuse" in selections:
# #         results["Landuse"] = landuse_analysis(df.copy())
# #     return results

# def process_pipeline(file_path: str, selections: List[str], thresholds: dict) -> dict:
#     df_original = read_file(file_path)
#     results = {}
#     if "AC Interference" in selections:
#         results["AC Interference"] = ac_interference_analysis(df_original)
#     if "ACPSP" in selections:
#         results["ACPSP"] = acpsp_analysis(df_original, thresholds.get("ACPSP", 4))
#     if "Attenuation" in selections:
#         results["Attenuation"] = attenuation_analysis(df_original, thresholds.get("Attenuation", 2))
#     if "CPCIPS" in selections:
#         results["CPCIPS"] = cpcips_analysis(df_original, thresholds.get("CPCIPS", -1.0))
#     if "Landuse" in selections:
#         results["Landuse"] = landuse_analysis(df_original)
#     return results


# # ---------------------------
# # API Endpoint
# # ---------------------------
# @app.post("/process-data/")
# async def process_data(
#     file: UploadFile = File(...),
#     selections: List[str] = Form(...),
#     acpsp_threshold: Optional[float] = Form(4),
#     attenuation_threshold: Optional[float] = Form(2),
#     cpcips_threshold: Optional[float] = Form(-1.0)
# ):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
#         tmp.write(await file.read())
#         tmp_path = tmp.name

#     thresholds = {
#         "ACPSP": acpsp_threshold,
#         "Attenuation": attenuation_threshold,
#         "CPCIPS": cpcips_threshold
#     }
#     results = process_pipeline(tmp_path, selections, thresholds)

#     output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
#     with pd.ExcelWriter(output_file) as writer:
#         for sheet_name, df in results.items():
#             df.to_excel(writer, index=False, sheet_name=sheet_name)

#     # return FileResponse(output_file, filename="Workbook.xlsx")
# from fastapi.responses import StreamingResponse

# def iterfile(file_path):
#     with open(file_path, mode="rb") as file_like:
#         yield from file_like

# return StreamingResponse(
#     iterfile(output_file),
#     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#     headers={"Content-Disposition": "attachment; filename=Workbook.xlsx"}
# )


# backend/main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import tempfile
import os
from typing import List, Optional

app = FastAPI()

# Allow CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://allied-engineers-dataextraction-2frontend.onrender.com"],  # Change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Helper: Read file
# ---------------------------
def read_file(file_path: str) -> pd.DataFrame:
    if file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format")

# ---------------------------
# AC Interference
# ---------------------------
def ac_interference_analysis(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip()
    df['Comment'] = df['Comment'].fillna('').astype(str)
    df['Normalized_Comment'] = df['Comment'].str.lower()

    base_keywords = ['ac interference']
    results = []
    start_row, start_index, current_keyword = None, None, None

    for i, row in df.iterrows():
        comment = row['Normalized_Comment'].strip().replace(';', '').strip()
        for keyword in base_keywords:
            if f"{keyword} start" in comment:
                start_row, start_index, current_keyword = row, i, keyword
                break
        if start_row is not None and f"{current_keyword} end" in comment:
            end_row, end_index = row, i
            attenuation_avg = df.loc[start_index:end_index, 'Attenuation'].mean()
            result = start_row.to_dict()
            result.update({
                'End VirtualDistance (m)': end_row.get('VirtualDistance (m)', ''),
                'End Latitude': end_row.get('Latitude', ''),
                'End Longitude': end_row.get('Longitude', ''),
                'Average Attenuation': attenuation_avg
            })
            if 'Station m' in df.columns:
                result['End Station m'] = end_row['Station m']
            results.append(result)
            start_row, current_keyword = None, None

    output_df = pd.DataFrame(results)
    output_df['Length (m)'] = output_df['End VirtualDistance (m)'] - output_df['VirtualDistance (m)']
    return output_df

# ---------------------------
# ACPSP Above Threshold
# ---------------------------
def acpsp_analysis(df: pd.DataFrame, threshold: float = 4) -> pd.DataFrame:
    if 'Station m' in df.columns:
        df['GAIL End Ch. (m)'] = df['Station m']

    df['XLI End Ch. (m)'] = df['VirtualDistance (m)']
    df['End Latitude'] = df['Latitude']
    df['End Longitude'] = df['Longitude']
    df['Above_Threshold'] = df['ACPSP_OnPotential'] > threshold

    def process_group(group):
        if group['Above_Threshold'].any():
            group['Highest_AC_PSP_V'] = group['ACPSP_OnPotential'].max()
            if len(group) > 1:
                if 'GAIL End Ch. (m)' in group.columns:
                    group.iloc[0, group.columns.get_loc('GAIL End Ch. (m)')] = group.iloc[-1]['GAIL End Ch. (m)']
                group.iloc[0, group.columns.get_loc('End Latitude')] = group.iloc[-1]['End Latitude']
                group.iloc[0, group.columns.get_loc('End Longitude')] = group.iloc[-1]['End Longitude']
                group.iloc[0, group.columns.get_loc('XLI End Ch. (m)')] = group.iloc[-1]['XLI End Ch. (m)']
        return group

    df = df.groupby((df['Above_Threshold'] != df['Above_Threshold'].shift()).cumsum(), group_keys=False).apply(process_group)
    df = df[df['Above_Threshold'] & (df['Above_Threshold'] != df['Above_Threshold'].shift())]
    df = df.drop(columns=['Above_Threshold'])
    df['Length (m)'] = df['XLI End Ch. (m)'] - df['VirtualDistance (m)']
    return df

# ---------------------------
# Attenuation Above Threshold
# ---------------------------
def attenuation_analysis(df: pd.DataFrame, threshold: float = 2) -> pd.DataFrame:
    df['End Latitude'] = df['Latitude']
    df['End Longitude'] = df['Longitude']
    df['XLI End Ch. (m)'] = df['VirtualDistance (m)']
    df['Above_Threshold'] = df['Attenuation'] > threshold

    def process_group(group):
        if group['Above_Threshold'].any():
            max_row = group.loc[group['Attenuation'].idxmax()]
            min_row = group.loc[group['Attenuation'].idxmin()]
            group['Average Attenuation'] = group['Attenuation'].mean()
            group['Max Attenuation Value'] = max_row['Attenuation']
            group['Min Attenuation Value'] = min_row['Attenuation']
        return group

    df = df.groupby((df['Above_Threshold'] != df['Above_Threshold'].shift()).cumsum(), group_keys=False).apply(process_group)
    df = df[df['Above_Threshold'] & (df['Above_Threshold'] != df['Above_Threshold'].shift())]
    df = df.drop(columns=['Above_Threshold'])
    df['Length (m)'] = df['XLI End Ch. (m)'] - df['VirtualDistance (m)']
    return df

# ---------------------------
# CPCIPS Below Threshold
# ---------------------------
def cpcips_analysis(df: pd.DataFrame, threshold: float = -1.0) -> pd.DataFrame:
    if 'Station m' in df.columns:
        df['GAIL End Ch. (m)'] = df['Station m']

    df['XLI End Ch. (m)'] = df['VirtualDistance (m)']
    df['End Latitude'] = df['Latitude']
    df['End Longitude'] = df['Longitude']
    df['Above_Threshold'] = df['CPCIPS_OnPotential'] < threshold

    def process_group(group):
        if group['Above_Threshold'].any():
            group['Lowest_CPCIPS_OnPotential'] = group['CPCIPS_OnPotential'].min()
        return group

    df = df.groupby((df['Above_Threshold'] != df['Above_Threshold'].shift()).cumsum(), group_keys=False).apply(process_group)
    df = df[df['Above_Threshold'] & (df['Above_Threshold'] != df['Above_Threshold'].shift())]
    df = df.drop(columns=['Above_Threshold'])
    df['Length (m)'] = df['XLI End Ch. (m)'] - df['VirtualDistance (m)']
    return df

# ---------------------------
# Landuse
# ---------------------------
def landuse_analysis(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip()
    df['Comment'] = df['Comment'].fillna('').astype(str)
    df['Normalized_Comment'] = df['Comment'].str.lower()

    base_keywords = [
        'road', 'surface pavement', 'gravel', 'surfaced pavement', 'gravel surface',
        'surfaced - pavement', 'surfaced-pavement', 'surface-pavement', 'rocky', 
        'cobble', 'surface - pavement', 'highway', 'railroad tracks'
    ]

    results = []
    start_row, start_index, current_keyword = None, None, None

    for i, row in df.iterrows():
        comment = row['Normalized_Comment']
        for keyword in base_keywords:
            if f"{keyword} start" in comment:
                start_row, start_index, current_keyword = row, i, keyword
                break
        if start_row is not None and f"{current_keyword} end" in comment:
            end_row, end_index = row, i
            attenuation_avg = df.loc[start_index:end_index, 'Attenuation'].mean()
            result = start_row.to_dict()
            result.update({
                'End Chainage (m)': end_row['VirtualDistance (m)'],
                'End Latitude': end_row['Latitude'],
                'End Longitude': end_row['Longitude'],
                'Average Attenuation': attenuation_avg
            })
            results.append(result)
            start_row, current_keyword = None, None

    output_df = pd.DataFrame(results)
    output_df['Length (m)'] = output_df['End Chainage (m)'] - output_df['VirtualDistance (m)']
    return output_df

# ---------------------------
# Process Pipeline
# ---------------------------
def process_pipeline(file_path: str, selections: List[str], thresholds: dict) -> dict:
    df = read_file(file_path)  # Read once
    results = {}
    if "AC Interference" in selections:
        results["AC Interference"] = ac_interference_analysis(df)
    if "ACPSP" in selections:
        results["ACPSP"] = acpsp_analysis(df, thresholds.get("ACPSP", 4))
    if "Attenuation" in selections:
        results["Attenuation"] = attenuation_analysis(df, thresholds.get("Attenuation", 2))
    if "CPCIPS" in selections:
        results["CPCIPS"] = cpcips_analysis(df, thresholds.get("CPCIPS", -1.0))
    if "Landuse" in selections:
        results["Landuse"] = landuse_analysis(df)
    return results

# ---------------------------
# API Endpoint
# ---------------------------
@app.post("/process-data/")
async def process_data(
    file: UploadFile = File(...),
    selections: List[str] = Form(...),
    acpsp_threshold: Optional[float] = Form(4),
    attenuation_threshold: Optional[float] = Form(2),
    cpcips_threshold: Optional[float] = Form(-1.0)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    thresholds = {
        "ACPSP": acpsp_threshold,
        "Attenuation": attenuation_threshold,
        "CPCIPS": cpcips_threshold
    }
    results = process_pipeline(tmp_path, selections, thresholds)

    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df in results.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)

    def iterfile(path):
        with open(path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(
        iterfile(output_file),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Workbook.xlsx"}
    )

