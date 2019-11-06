#!/usr/bin/env python3
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak, Frame, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen.canvas import Canvas
import re
import json
from pathlib import Path

index = {}
pageNum = 0
DESCENDERS = ["g", "j", "p", "y"]
doc = SimpleDocTemplate("demo3.pdf",
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)

Story = []
stylesheet = getSampleStyleSheet()

def make_cultures_page(map_file):
    global pageNum

    cultures_list = None
    for line in map_file:
        result = re.match('\[\{"name":"Wildlands".*', line)
        if result != None:
            cultures_line = result[0]
            cultures_list = json.loads(cultures_line)
            break

    pdf.add_page()
    pageNum += 1
    index[pdf.page_no()] = "Cultures"


    pdf.set_font("Times", size=72)
    pdf.cell(EPW, 60, "Cultures", align = "C")

    pdf.set_font("Times", size=18)
    pdf.set_xy(14, 75)

    first_lock = False
    pdf.set_line_width(2)
    for culture in cultures_list:
        if ("removed" not in culture) and (culture['area'] > 0):
            if first_lock:
                pdf.set_x(14)
            else:
                first_lock = True
            if "color" in culture:
                pdf.set_draw_color(*h2d(culture['color']))
            else:
                pdf.set_draw_color(0, 0, 0)

            pdf.cell(EPW/4, 10, f"Name: {culture['name']}", 1, 0)
            pdf.cell(EPW/4, 10, f"Area: {culture['area']}", 1, 2)
            pdf.set_y(pdf.get_y() + 2)


def make_religions_page():
    global pageNum
    pdf.add_page()
    pageNum += 1
    index[pdf.page_no()] = "Relgions"

    pdf.set_font("Times", size=72)
    pdf.cell(EPW, 60, "Religions", align = "C")

    pdf.set_font("Times", size=18)
    pdf.set_xy(8, 55)

    pdf.set_line_width(1)
    RELIGIONS_RIGHT_PADDING = 9.8
    first_lock = False
    for religion in religions:
        if ("origin" in religion) and (religion["origin"] != 0):
            if first_lock:
                pdf.set_x(8)
            else:
                first_lock = True
            if "color" in religion:
                pdf.set_draw_color(*h2d(religion['color']))
            else:
                pdf.set_draw_color(0, 0, 0)

            if religion["name"] != "No religion":
                # Name, Form
                #  Deity, type
                pdf.cell(EPW/3 + EPW/3, 10, f"{religion['name']}", 1, 0)
                pdf.cell(EPW/3, 10, f"Form: {religion['form']}", 1, 1)
                pdf.set_x(14)
                pdf.cell(EPW/3 + EPW/3, 10, f"Deity: {religion['deity']}", 1, 0)
                pdf.cell(EPW/4 + RELIGIONS_RIGHT_PADDING, 10, f"{religion['type']}", 1, 2)
                pdf.set_y(pdf.get_y() + 1)


def make_nation_page(nation):
    """Create the basic page for every nation.

    This page contains key info as well as the nation's name and color.
    Then, additional sections are added end of the function.
    """
    global pageNum, index

    # Record where this page is, update total page count
    index[pageNum] = nation["name"]
    pageNum += 1

    # Write the nation's name in its color
    nation_color = nation["color"]
    nationTable = [[],[]]
    """
    Key info    | Province      | Diplomacy
    actual info | Province list | dip list
    """
    p = Paragraph(nation['name'], style = stylesheet["Title"])
    Story.append(p)

    # Make Title
    p2 = Paragraph("Key Info", style = stylesheet["Heading1"])
    nationTable[0].append(p2)

    #Retrieve burg information
    filtered_burgs = filter_burgs(nation['i'])
    capital = "No Captial Found"
    population = 0
    for burg in filtered_burgs:
        if burg['capital']:
            capital = burg['name']

    # Print all key info
    p3 = Paragraph(
        f"""
            • Capital: {capital}<br/>
            • Burgs: {nation['burgs']}<br/>
            • Area (mi^2): {nation['area']}
        """, style= stylesheet["Normal"])
    nationTable[1].append(p3)

    # Add additional sections
    prov = Paragraph("Provinces", style = stylesheet["Heading1"])
    nationTable[0].append(prov)
    nationTable[1].append(make_provinces_section(nation["i"]))

    dip = Paragraph("Diplomacy", style = stylesheet["Heading1"])
    nationTable[0].append(dip)

    nationTable[1].append(make_relation_section(nation["diplomacy"]))
    nationT = Table(nationTable)
    nationT.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),]))
    Story.append(nationT)
    Story.append(PageBreak())



def make_relation_section(relations):
    """Add a relations section to the nation's page that details
    relations with all other nations.
    """
    data = []

    for i, curr_nation_name in enumerate(nation_names):
        # Skip all nations that aren't actually on the map. Area = 0 or is removed.
        if i not in deleted_nations:
            # Target nation and their relation with curr_nation.
            data.append((curr_nation_name, relations[i]))

    relations_table = Table(data)
    relations_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, (0, 0, 0)),
        ('INNERGRID', (0,0), (-1, -1), 2, (0,255,0))
        ]))
    return relations_table


def make_provinces_section(curr_nation_id):
    """Add a provinces section to the nation's page to show all
    active provinces within the nation.
    """

    # Select only the provinces that are inside of curr_nation_id
    curr_provinces = [province for province in provinces if province['state'] == curr_nation_id]
    data = []
    for province in curr_provinces:
        # {form} of {name} OR {fullName}
        # EX: Barony of Elvelavo
        if province['fullName'] != province['name']:
            data.append(province['fullName'])
        else:
            data.append(f"{province['formName']} of {province['name']}")

    province_paragraph = Paragraph('<br/>'.join(data), style = stylesheet["Normal"])
    return province_paragraph



def make_toc():
    pdf.page = 1
    pdf.set_font("Times", size=72)
    pdf.cell(EPW, 60, "Table of Contents", align = "C")
    pdf.set_font("Times", size=18)
    for page in index:
        pdf.cell(EPW/4, 10, f"A", border=1, ln=0)
        pdf.cell(EPW/10, 10, f"B", border=1, ln=1)


def filter_map(pattern):
    result = None
    for line in map_file:
        matched = re.match(pattern, line)
        if matched != None:
            result = json.loads(matched[0])

    return result


def filter_burgs(id):
    result = []

    for burg in burgs:
        if 'state' in burg:
            if burg["state"] == id:
                result.append(burg)

    return result

def setupPage(canvas, doc):
    canvas.saveState()
    canvas.drawImage("scroll_background.jpg", 0, 0)
    canvas.restoreState()

map_files = [pth for pth in Path.cwd().iterdir() if pth.suffix == ".map"]
for file in map_files:
    map_file = open(file, 'r').readlines()

    # Make the Cultures Overview page
    #make_cultures_page(map_file)

    nations = filter_map('\[\{"i":0,"name":"Neutrals".*')
    burgs = filter_map('\[\{\},\{"cell":.*')
    provinces = filter_map('\[0,\{"i":1,"state":.*')
    religions = filter_map('\[\{"i":0,"name":"No religion"\}.*')
    provinces.remove(0)

    #make_religions_page()
    nation_names = [nation["name"] for nation in nations]
    nation_ids = []
    deleted_nations = []

    for nation in nations:
        if (nation['area'] != 0) and ('removed' not in nation):
            make_nation_page(nation)
            nation_ids.append(nation["i"])
        else:
            deleted_nations.append(nation["i"])

    print(
        f"Finished making x pages about all {len(nation_ids)} nations.")
    doc.build(Story, onFirstPage=setupPage, onLaterPages=setupPage)
