from fpdf import FPDF
#from fpdf.html import hex2dec as h2d
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch as INCH
import pandas as pd
import re
import json
from pathlib import Path

index = {}
pageNum = 0
c = canvas.Canvas("demo2.pdf")
c_width, c_height = A4

textobject = c.beginText()
textobject.setTextOrigin(INCH, 2.5*INCH)
textobject.setFont("Times-Roman", 12)

EPW = c_width - 2*INCH
DESCENDERS = ["g", "j", "p", "y"]


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


def make_nation_page(nation, c):
    """Create the basic page for every nation.

    This page contains key info as well as the nation's name and color.
    Then, additional sections are added end of the function.
    """
    global pageNum, index

    c.setFont("Times-Roman", 72)
    c.line(INCH, INCH, INCH, c_height - INCH)
    c.line(c_width - INCH, INCH, c_width - INCH, c_height - INCH)

    c.line(c_width - INCH, INCH, INCH, INCH)
    c.line(c_width - INCH, c_height - INCH, INCH, c_height - INCH)

    # Record where this page is, update total page count
    index[pageNum] = nation["name"]
    pageNum += 1

    # Write the nation's name in its color
    nation_color = nation["color"]
    c.drawCentredString(EPW/2 + 70, c_height - INCH - 50, nation["name"])

    # DESCENDERS adjustment
    title_y = 51
    if any(descender in nation["name"] for descender in DESCENDERS):
        title_y += 15

    c.setLineWidth(5)
    c.setStrokeColor(nation_color)
    c.line(0, c_height - INCH - title_y, c_width, c_height - INCH - title_y)
    c.setLineWidth(1)

    t = c.beginText()

    # Make Title
    t.setTextOrigin(INCH + 10, c_height - INCH - title_y * 2)
    t.setFont("Times-Roman", 36)
    t.textLine("Key Info")

    # Return to normal
    t.setFont("Times-Roman", 18)
    t.moveCursor(0, -10)

    #Retrieve burg information
    filtered_burgs = filter_burgs(nation['i'])
    capital = "No Captial Found"
    population = 0
    for burg in filtered_burgs:
        if burg['capital']:
            capital = burg['name']

    # Print all key info
    t_y = t.getY() - 30
    t.textLine(f"Capital: {capital}")
    t.textLine(f"Burgs: {nation['burgs']}")
    t.textLine(f"Area (mi^2): {nation['area']}")

    # Store it inside a box
    c.setLineWidth(5)
    c.rect(INCH + 7, t_y, 170, 70)
    c.setLineWidth(1)
    c.drawText(t)

    # Add additional sections
    #make_provinces_section(nation["i"])
    #make_relation_section(nation["diplomacy"])


def make_relation_section(relations):
    """Add a relations section to the nation's page that details
    relations with all other nations.
    """

    # Create the section header
    pdf.set_xy(15, 120)
    pdf.set_font("Times", size=36)
    pdf.cell(30, 20, "Relations")

    # Return to normal
    pdf.set_xy(8, 135)
    pdf.set_font("Times", size=12)
    pdf.set_draw_color(0, 0, 0)

    first_nation_lock = False

    for i, curr_nation_name in enumerate(nation_names):
        if first_nation_lock:
            pdf.set_x(8)
        else:
            first_nation_lock = True

        height = pdf.font_size + 1

        # Skip all nations that aren't actually on the map. Area = 0 or is removed.
        if i not in deleted_nations:
            # If letter is a descender, increase space allowed.
            if any((descender in curr_nation_name) or (descender in relations[i]) for
                    descender in DESCENDERS):
                height += 1

            # Target nation and their relation with curr_nation.
            pdf.cell(EPW/4, height, f"{curr_nation_name}", border=1, ln=0)
            pdf.cell(EPW/10, height, f"{relations[i]}", border=1, ln=1)


def make_provinces_section(curr_nation_id):
    """Add a provinces section to the nation's page to show all
    active provinces within the nation.
    """

    # Select only the provinces that are inside of curr_nation_id
    curr_provinces = [province for province in provinces if province['state'] == curr_nation_id]

    # Make Header
    pdf.set_xy(120, 55)
    pdf.set_font("Times", size=36)
    pdf.cell(30, 20, "Provinces")

    # Return to normal
    pdf.set_xy(100, 70)
    pdf.set_font("Times", size=12)

    for province in curr_provinces:
        # Grab row, convert to array, set borders to province color
        th = pdf.font_size + 1
        pdf.set_x(85)
        pdf.set_draw_color(*h2d(province['color']))

        # Compensate for DESCENDERS
        if any((descender in province['formName']) or (descender in province['name']) for descender in DESCENDERS):
            th += 1

        # {form} of {name}
        # EX: Barony of Elvelavo
        if province['fullName'] != province['name']:
            pdf.cell(EPW/4, th, f"{province['fullName']}", 1, 2)
        else:
            pdf.cell(EPW/4, th, f"{province['formName']} of {province['name']}", 1, 2)

        pdf.set_y(pdf.get_y() + 1)


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
            c.showPage()
            make_nation_page(nation, c)
            nation_ids.append(nation["i"])
        else:
            deleted_nations.append(nation["i"])

    #print(index)
    #make_toc()

    print(
        f"Finished making x pages about all {len(nation_ids)} nations.")
    c.save()

#NOTES
#canvas.bookmarkPage(name)
