from fpdf import FPDF
from fpdf.html import hex2dec as h2d
import pandas as pd
import re
import json

class PDF(FPDF):
    def header(self):
        # Set background image
        pdf.image("data/scroll_background.jpg", 0, 0)

nationStarts = {}
pageNum = 0
pdf = PDF()

EPW = pdf.w - 2*pdf.l_margin
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

    pdf.set_font("Times", size=72)
    pdf.cell(EPW, 60, "Cultures", align = "C")

    pdf.set_font("Times", size=18)
    pdf.set_xy(14, 75)

    counter = 0
    pdf.set_line_width(2)
    for culture in cultures_list:
        if ("removed" not in culture) and (culture['area'] > 0):
            if counter > 0:
                pdf.set_x(14)
            if "color" in culture:
                pdf.set_draw_color(*h2d(culture['color']))
            else:
                pdf.set_draw_color(0, 0, 0)

            pdf.cell(EPW/4, 10, f"Name: {culture['name']}", 1, 0)
            pdf.cell(EPW/4, 10, f"Area: {culture['area']}", 1, 2)
            counter += 1

def make_religions_page():
    global pageNum
    pdf.add_page()
    pageNum += 1

    pdf.set_font("Times", size=72)
    pdf.cell(EPW, 60, "Religions", align = "C")

    pdf.set_font("Times", size=18)
    pdf.set_xy(14, 55)

    counter = 0
    pdf.set_line_width(1)
    for religion in religions:
        if ("origin" in religion) and (religion["origin"] != 0):
            if counter > 0:
                pdf.set_x(14)
            if "color" in religion:
                pdf.set_draw_color(*h2d(religion['color']))
            else:
                pdf.set_draw_color(0, 0, 0)

            if religion["name"] != "No religion":
                pdf.cell(EPW/3, 10, f"{religion['name']}", 1, 0)
                pdf.cell(EPW/4, 10, f"{religion['form']}", 1, 0)
                pdf.cell(EPW/4, 10, f"Type: {religion['type']}", 1, 1)
                pdf.set_x(14)
                pdf.cell(EPW/3 + EPW/4, 10, f"{religion['deity']}", 1, 2)
            counter += 1


def make_nation_page(nation):
    """Create the basic page for every nation.

    This page contains key info as well as the nation's name and color.
    Then, additional sections are added end of the function.
    """
    global pageNum, nationStarts

    pdf.set_line_width(3)

    pdf.set_font("Times", size=72)
    pdf.add_page()

    # Set background image
    pdf.image("data/scroll_background.jpg", 0, 0)

    # Write the nation's name in its color
    nation_color = h2d(nation["color"])
    pdf.cell(EPW, 60, nation["name"], align="C")
    pdf.set_draw_color(*nation_color)

    # DESCENDERS adjustment
    title_y = 51
    if any(descender in nation["name"] for descender in DESCENDERS):
        title_y += 5

    pdf.line(0, title_y, 500, title_y)

    # Make Title
    pdf.set_xy(15, 55)
    pdf.set_font("Times", size=36)
    pdf.cell(30, 20, "Key Info")

    # Return to normal
    pdf.set_font("Times", size=18)
    pdf.set_xy(14, 75)

    #Retrieve burg information
    filtered_burgs = filter_burgs(nation['i'])
    capital = "No Captial Found"
    population = 0
    for burg in filtered_burgs:
        if burg['capital']:
            capital = burg['name']

    # Print all key info
    frame_key_info_y = pdf.get_y()
    pdf.cell(0, 10, f"Capital: {capital}", 0, 2)
    pdf.cell(0, 10, f"Burgs: {nation['burgs']}", 0, 2)
    pdf.cell(0, 10, f"Area (mi^2): {nation['area']}", 0, 1)
    frame_key_info_y2 = pdf.get_y()

    # Store it inside a box
    pdf.set_xy(12, 75)
    pdf.cell(65, frame_key_info_y2 - frame_key_info_y, border=1)

    # Record where this page is, update total page count
    nationStarts[nation["name"]] = pdf.page_no()
    pageNum = pdf.page_no()

    # Add additional sections
    pdf.set_line_width(1)
    make_provinces_section(nation["i"])
    make_relation_section(nation["diplomacy"])


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


# MAIN
pdf.set_font("Times", size=12)

# Load the map file
map_file = open('data/map_file.map', 'r').readlines()

# Make the Cultures Overview page
make_cultures_page(map_file)

nations = filter_map('\[\{"i":0,"name":"Neutrals".*')
burgs = filter_map('\[\{\},\{"cell":.*')
provinces = filter_map('\[0,\{"i":1,"state":.*')
religions = filter_map('\[\{"i":0,"name":"No religion"\}.*')
provinces.remove(0)

make_religions_page()
nation_names = [nation["name"] for nation in nations]
nation_ids = []
deleted_nations = []

for nation in nations:
    if (nation['area'] != 0) and ('removed' not in nation):
        make_nation_page(nation)
        nation_ids.append(nation["i"])
    else:
        deleted_nations.append(nation["i"])

# Write to PDF, and say we are finished.
pdf.output("demo.pdf")
print(
    f"Finished making {pageNum} pages about all {len(nation_ids)} nations.")