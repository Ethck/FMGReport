from fpdf import FPDF
from fpdf.html import hex2dec as h2d
import pandas as pd

#CONSTANTS
pdf = FPDF()
CENTER = pdf.w - 2*pdf.l_margin
BAD_LETTERS = ["g", "j", "y"]

#Active Variables
stateStarts = {}
pageNum = 0
#FUNCTIONS
def makeStatePage(state):
	global pageNum

	pdf.set_font("Times", size=72)
	pdf.add_page()

	state_color = h2d(state["Color"])
	pdf.cell(CENTER, 60, state["State"], align="C")
	pdf.set_draw_color(*state_color)

	if any(badLetter in state["State"] for badLetter in BAD_LETTERS):
		pdf.line(0,56,500,56)
	else:
		pdf.line(0,51,500,51)

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

#MAIN
pdf.set_font("Times", size=12)

states = pd.read_csv("states_data_test.csv")
states.drop(states.tail(1).index, inplace=True)
pdf.set_line_width(5)
states.apply(makeStatePage, axis=1)

print(f"Finished making {pageNum} pages.")


pdf.output("demo.pdf")