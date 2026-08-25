from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def read_csv_with_fallback(path: Path) -> tuple[pd.DataFrame, str]:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "cp949", "euc-kr", "utf-8"):
        try:
            return pd.read_csv(path, encoding=encoding, dtype=str, keep_default_na=False), encoding
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError("could not decode CSV: " + "; ".join(errors))


def _find_column(columns: list[str], terms: tuple[str, ...]) -> str | None:
    for column in columns:
        normalized = column.lower().replace(" ", "")
        if any(term in normalized for term in terms):
            return column
    return None


def _find_projected_pair(columns: list[str]) -> tuple[str | None, str | None]:
    x_column = _find_column(columns, ("좌표정보(x)", "좌표정보x", "x좌표", "longitude_x"))
    y_column = _find_column(columns, ("좌표정보(y)", "좌표정보y", "y좌표", "latitude_y"))
    return x_column, y_column


def _numeric_quality(frame: pd.DataFrame, column: str | None) -> dict[str, float | int | None]:
    if not column:
        return {"column": None, "nonempty_count": 0, "numeric_valid_count": 0, "invalid_or_null_rate": 1.0}
    values = frame[column].astype(str).str.strip()
    nonempty = values != ""
    numeric = pd.to_numeric(values, errors="coerce")
    nonempty_count = int(nonempty.sum())
    valid_count = int((nonempty & numeric.notna()).sum())
    return {
        "column": column,
        "nonempty_count": nonempty_count,
        "numeric_valid_count": valid_count,
        "invalid_or_null_rate": float(1 - (valid_count / len(frame))) if len(frame) else 1.0,
    }


def audit_csv(path: Path) -> dict[str, Any]:
    frame, encoding = read_csv_with_fallback(path)
    columns = [str(column) for column in frame.columns]
    text = frame.fillna("").astype(str)
    anyang_mask = text.apply(lambda row: row.str.contains("안양|Anyang", case=False, regex=True).any(), axis=1)
    lat_column = _find_column(columns, ("위도", "latitude", "lat"))
    lon_column = _find_column(columns, ("경도", "longitude", "lon"))
    projected_x, projected_y = _find_projected_pair(columns)
    coordinate_valid_count = 0
    if lat_column and lon_column:
        lat = pd.to_numeric(frame[lat_column], errors="coerce")
        lon = pd.to_numeric(frame[lon_column], errors="coerce")
        coordinate_valid_count = int((lat.between(-90, 90) & lon.between(-180, 180)).sum())
    projected_coordinate_valid_count = 0
    if projected_x and projected_y:
        x = pd.to_numeric(frame[projected_x], errors="coerce")
        y = pd.to_numeric(frame[projected_y], errors="coerce")
        projected_coordinate_valid_count = int((x.notna() & y.notna()).sum())
    capacity_column = _find_column(columns, ("최대수용인원", "수용인원", "capacity", "물량", "급수량"))
    null_rates = {
        column: float((text[column].str.strip() == "").mean())
        for column in columns
    }
    return {
        "path": path.as_posix(),
        "encoding": encoding,
        "raw_row_count": int(len(frame)),
        "anyang_row_count": int(anyang_mask.sum()),
        "columns": columns,
        "coordinate_columns": {"latitude": lat_column, "longitude": lon_column},
        "coordinate_valid_count": coordinate_valid_count,
        "projected_coordinate_columns": {"x": projected_x, "y": projected_y},
        "projected_coordinate_valid_count": projected_coordinate_valid_count,
        "numeric_quality": {"capacity": _numeric_quality(frame, capacity_column)},
        "null_rates": null_rates,
        "anyang_sample_records": frame.loc[anyang_mask].head(3).to_dict(orient="records"),
    }
