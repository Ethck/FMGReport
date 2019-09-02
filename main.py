from fpdf import FPDF
from fpdf.html import hex2dec as h2d
import pandas as pd

#CONSTANTS
pdf = FPDF()
EPW = pdf.w - 2*pdf.l_margin
BAD_LETTERS = ["g", "j", "y", "p"]

#Active Variables
stateStarts = {}
pageNum = 0

#FUNCTIONS
def makeStatePage(state, relations):
	global pageNum, stateStarts

	pdf.set_line_width(3)

	pdf.set_font("Times", size=72)
	pdf.add_page()

	state_color = h2d(state["Color"])
	pdf.cell(EPW, 60, state["State"], align="C")
	pdf.set_draw_color(*state_color)

	if any(badLetter in state["State"] for badLetter in BAD_LETTERS):
		pdf.line(0,56,500,56)
	else:
		pdf.line(0,51,500,51)

	pdf.set_xy(15, 52)
	pdf.set_font("Times", size=36)
	pdf.cell(30, 20, "Key Info")


	pdf.set_font("Times", size=18)
	pdf.set_xy(10,70)

	frame_key_info_y = pdf.get_y()
	pdf.cell(0, 10, f"Capital: {state['Capital']}", 0, 2)
	pdf.cell(0, 10, f"Burgs: {state['Burgs']}", 0, 2)
	pdf.cell(0, 10, f"Area (mi^2): {state['Area mi2']}", 0, 2)
	pdf.cell(0, 10, f"Population: {state['Population']}", 0, 1)
	frame_key_info_y2 = pdf.get_y()

	pdf.set_xy(8, 70)
	pdf.cell(65, frame_key_info_y2 - frame_key_info_y , border = 1)

	stateStarts[state["State"]] = pdf.page_no()
	pageNum = pdf.page_no()

	makeRelationSection(relations[state["State"]], state["State"])
	makeProvincialSection(state["State"])

def makeRelationSection(relations, curr_state):
	pdf.set_line_width(1)
	pdf.set_xy(15, 120)
	pdf.set_font("Times", size=36)
	pdf.cell(30, 20, "Relations")
	pdf.set_xy(8, 135)
	pdf.set_font("Times", size=12)

	global stateNames
	for i, state in enumerate(stateNames):
		if i >= 1:
			pdf.set_x(8)

		th = pdf.font_size + 1

		if any((badLetter in state) or (badLetter in relations[i]) for badLetter in BAD_LETTERS):
			th + 1

		pdf.cell(EPW/4, th, f"{state}", border=1, ln= 0)
		pdf.cell(EPW/10, th, f"{relations[i]}", border=1, ln=1)

def makeProvincialSection(curr_state):
	selection = provincesDF.loc[provincesDF["State"] == curr_state]
	pdf.set_xy(120, 55)
	pdf.set_font("Times", size=36)
	pdf.cell(30, 20, "Provinces")

	pdf.set_xy(100, 70)
	pdf.set_font("Times", size=12)
	for i in range(len(selection.index)):
		th = pdf.font_size + 1
		pdf.set_x(90)
		row = selection.iloc[[i]].to_numpy()[0]
		pdf.set_draw_color(*h2d(row[4]))

		if any((badLetter in row[2]) for badLetter in BAD_LETTERS):
			th += 1

		pdf.cell(EPW/4, th, f"{row[2]} of {row[1]}", 1, 0)
		pdf.cell(EPW/8, th, f"Area: {row[6]}", 1, 0)
		pdf.cell(EPW/4, th, f"Pop.: {row[7]}", 1, 2)



#MAIN
pdf.set_font("Times", size=12)

relationsDF = pd.read_csv("data/state_relations_data_test.csv")
relationsDF = relationsDF.sort_values(by = "Target")
stateNames = relationsDF['Target'].tolist()

provincesDF = pd.read_csv("data/provinces_data_test.csv")

states = pd.read_csv("data/states_data_test.csv")
states.drop(states.tail(1).index, inplace=True)
states.apply(makeStatePage, axis=1, relations = relationsDF)

#relationsDF.apply(makeRelationSection, axis=1)
print(stateNames)


pdf.output("demo.pdf")
print(f"Finished making {pageNum} pages.")