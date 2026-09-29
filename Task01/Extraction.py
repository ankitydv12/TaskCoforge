import pdfplumber

from schema import Document

documents = []

def outside_tables(obj, table_regions):
    if not all(k in obj for k in ("x0", "x1", "top", "bottom")):
        return True

    for x0, top, x1, bottom in table_regions:
        if (
        obj["x0"] >= x0
        and obj["x1"] <= x1
        and obj["top"] >= top
        and obj["bottom"] <= bottom
        ):
            return False
    return True

with pdfplumber.open(r"D:\Task01ChunkStra\Task01\uploads\India-Leave-Policy.pdf") as pdf:
    for page_no , page in enumerate(pdf.pages[2:], start=3 ):
        print(f"Page No --> {page_no}")
        tables = page.find_tables()
        table_regions = [table.bbox for table in tables]
        filtered_page = page.filter(
            lambda obj: outside_tables(obj, table_regions))
        texts = filtered_page.extract_text()

        documents.append(
            Document(texts,{"page_no":page_no, "content_type": "str" })
        )

        tables = page.extract_tables({
                "vertical_strategy": "lines_strict",
                "horizontal_strategy": "lines_strict",
                "snap_tolerance" : 3,
                "join_tolerance" : 2,
                "intersection_tolerance" : 4
        })

        

        image = page.to_image()
        image.debug_tablefinder(table_settings={})
        image.show()


        print(len(tables))
     
        for table in tables:
            for row in table:
                print(row)
            