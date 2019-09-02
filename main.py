from fpdf import FPDF
from fpdf.html import hex2dec as h2d
import pandas as pd

nationStarts = {}
pageNum = 0
pdf = FPDF()

EPW = pdf.w - 2*pdf.l_margin
DESCENDERS = ["g", "j", "y", "p"]


def make_nation_page(nation, relations):
    """Create the basic page for every nation.

    This page contains key info as well as the nation's name and color.
    Then, additional sections are added end of the function.
    """
    global pageNum, nationStarts

    pdf.set_line_width(3)

    pdf.set_font("Times", size=72)
    pdf.add_page()

    #Set background image
    pdf.image("data/scroll_background.jpg", 0, 0)

    #Write the nation's name in its color
    nation_color = h2d(nation["Color"])
    pdf.cell(EPW, 60, nation["State"], align="C")
    pdf.set_draw_color(*nation_color)

    #DESCENDERS adjustment
    title_y = 51
    if any(descender in nation["State"] for descender in DESCENDERS):
        title_y += 5

    pdf.line(0, title_y, 500, title_y)

    #Make Title
    pdf.set_xy(15, 52)
    pdf.set_font("Times", size=36)
    pdf.cell(30, 20, "Key Info")

    #Return to normal
    pdf.set_font("Times", size=18)
    pdf.set_xy(10,70)

    #Print all key info
    frame_key_info_y = pdf.get_y()
    pdf.cell(0, 10, f"Capital: {nation['Capital']}", 0, 2)
    pdf.cell(0, 10, f"Burgs: {nation['Burgs']}", 0, 2)
    pdf.cell(0, 10, f"Area (mi^2): {nation['Area mi2']}", 0, 2)
    pdf.cell(0, 10, f"Population: {nation['Population']}", 0, 1)
    frame_key_info_y2 = pdf.get_y()

    #Store it inside a box
    pdf.set_xy(8, 70)
    pdf.cell(65, frame_key_info_y2 - frame_key_info_y , border = 1)

    #Record where this page is, update total page count
    nationStarts[nation["State"]] = pdf.page_no()
    pageNum = pdf.page_no()

    #Add additional sections
    pdf.set_line_width(1)
    make_relation_section(relations[nation["State"]], nation["State"])
    make_provinces_section(nation["State"])


def make_relation_section(relations, curr_nation):
    """Add a relations section to the nation's page that details
    relations with all other nations.
    """

    #Create the section header
    pdf.set_xy(15, 120)
    pdf.set_font("Times", size=36)
    pdf.cell(30, 20, "Relations")

    #Return to normal
    pdf.set_xy(8, 135)
    pdf.set_font("Times", size=12)
    pdf.set_draw_color(0, 0, 0)

    global nation_names
    for i, nation in enumerate(nation_names):
        if i >= 1:
            pdf.set_x(8)

        height = pdf.font_size + 1

        #If letter is a descender, increase space allowed.
        if any((descender in nation) or (descender in relations[i]) for
                descender in DESCENDERS):
            height += 1

        #Target nation and their relation with curr_nation.
        pdf.cell(EPW/4, height, f"{nation}", border=1, ln= 0)
        pdf.cell(EPW/10, height, f"{relations[i]}", border=1, ln=1)


def make_provinces_section(curr_nation):
    """Add a provinces section to the nation's page to show all
    active provinces within the nation.
    """

    #Select only the provinces that are inside of curr_nation
    selection = provinces_DF.loc[provinces_DF["State"] == curr_nation]

    #Make Header
    pdf.set_xy(120, 55)
    pdf.set_font("Times", size=36)
    pdf.cell(30, 20, "Provinces")

    #Return to normal
    pdf.set_xy(100, 70)
    pdf.set_font("Times", size=12)

    for i in range(len(selection.index)):
        #Grab row, convert to array, set borders to province color
        th = pdf.font_size + 1
        pdf.set_x(85)
        row = selection.iloc[[i]].to_numpy()[0]
        pdf.set_draw_color(*h2d(row[4]))

        #Compensate for DESCENDERS
        if any((descender in row[2]) for descender in DESCENDERS):
            th += 1

        #{form} of {name} | {area} | {population}
        #EX: Barony of Elvelavo | 5.4k | 113k
        pdf.cell(EPW/4, th, f"{row[2]} of {row[1]}", 1, 0)
        pdf.cell(EPW/7, th, f"Area: {row[6]}", 1, 0)
        pdf.cell(EPW/4, th, f"Pop.: {row[7]}", 1, 2)


#MAIN
pdf.set_font("Times", size=12)

#Load relations, sort to alphabetical by origin nation
relations_DF = pd.read_csv("data/state_relations_data_test.csv")
relations_DF = relations_DF.sort_values(by = "Target")
nation_names = relations_DF['Target'].tolist()

#Load provinces
provinces_DF = pd.read_csv("data/provinces_data_test.csv")

#Load nations, drop the neutrals row, for each nation make a page
nations = pd.read_csv("data/states_data_test.csv")
nations.drop(nations.tail(1).index, inplace=True)
nations.apply(make_nation_page, axis=1, relations = relations_DF)

#Write to PDF, and say we are finished.
pdf.output("demo.pdf")
print(
    f"Finished making {pageNum} pages about all {len(nation_names)} nations.")