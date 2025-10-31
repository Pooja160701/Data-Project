import os
import pandas as pd
from bs4 import BeautifulSoup
import re

folder_path = "Question1"
html_files = ["first.html", "second.html", "third.html"]

FIELDS = [
    "Price", "Depreciation", "Reg Date", "Mileage", "Manufactured",
    "Road Tax", "Transmission", "Dereg Value", "OMV", "COE", "ARF",
    "Engine Cap", "Power", "Curb Weight", "No. of Owners", "Type of Vehicle"
]


def clean_text(text):
    if not text:
        return None
    text = text.replace("\xa0", " ")
    text = re.sub(r"View models.*", "", text)
    text = re.sub(r"\(change\)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_fields(info_table):
    data = {}

    for row in info_table.find_all("tr"):
        tds = row.find_all("td")

        for i, td in enumerate(tds):
            strong_tag = td.find("strong")
            if strong_tag:
                label = clean_text(strong_tag.get_text())

                value = None
                if i + 1 < len(tds):
                    value = clean_text(tds[i + 1].get_text(" ", strip=True))

                if not value:
                    div_parent = strong_tag.find_parent("div", class_="row_title")
                    if div_parent:
                        info_div = div_parent.find_next_sibling("div", class_="row_info")
                        if info_div:
                            value = clean_text(info_div.get_text(" ", strip=True))

                if label == "Reg Date" and not value:
                    next_td = td.find_next_sibling("td")
                    if next_td:
                        value = clean_text(next_td.get_text(" ", strip=True))

                if label in FIELDS and value:
                    data[label] = value

        for each_info in row.find_all("div", class_="eachInfo"):
            title_div = each_info.find("div", class_="row_title")
            info_div = each_info.find("div", class_="row_info")
            if title_div and info_div:
                label_tag = title_div.find("strong") or title_div.find("a")
                if label_tag:
                    label = clean_text(label_tag.get_text())
                    if label in FIELDS:
                        data[label] = clean_text(info_div.get_text(" ", strip=True))

        if "Type of Vehicle" in row.get_text():
            strong_tag = row.find("strong", string="Type of Vehicle")
            if strong_tag:
                next_td = strong_tag.find_parent("td").find_next_sibling("td")
                if next_td:
                    data["Type of Vehicle"] = clean_text(next_td.get_text())

    return data

records = []
for file in html_files:
    file_path = os.path.join(folder_path, file)
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

        car_data = {"File": file}
        info_table = soup.find("table", {"id": "carInfo"})
        if info_table:
            fields_data = extract_fields(info_table)
            for f_name in FIELDS:
                car_data[f_name] = fields_data.get(f_name, None)

        records.append(car_data)

df = pd.DataFrame(records)
df = df[["File"] + FIELDS]
print(df)

df.to_csv("car_data.csv", index=False)