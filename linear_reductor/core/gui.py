import PySimpleGUI as sg 
from main import run_reductor, read_sigma
from fractions import Fraction
from solver import find_reductions
from base_logger import logger
import logging

sg.theme('Dark Amber') # Add some color

# Redirect logs to debug window

class GuiHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        sg.Print(str(record).strip())

ch = GuiHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)



# 1- the layout
layout = [[sg.Text('Sigma:', size=(15,1)), sg.Input(key='-IN_SIGMA-', size=(32,1), default_text="[0, 1/3) U (1/3, 1]")],
          [sg.Text('(Alpha) Active >=', size=(15,1)), sg.Input(key='-IN_ALPHA-', size=(32,1), default_text="1")],
          [sg.Text('(Beta) Passive <=', size=(15,1)), sg.Input(key='-IN_BETA-', size=(32,1), default_text="1")],
          [sg.Text('epsilon', size=(15,1)), sg.Input(key='-IN_EPSILON-', default_text=0.0001, size=(32,1))],
          [sg.Text('d, delta:', size=(15,1)), sg.Input(key='-IN_D-', size=(2,1), default_text=3), sg.Input(key='-IN_DELTA-', size=(2,1), default_text=3)],
          [sg.Button('Find reductions', size=(15,1)), sg.Button('Exit', size=(15,1))],
          [sg.Output(size = (100,10), key = '-OUTPUT-')],
          [sg.Button("Harden problem", key = "-HARDEN-", size=(15,1), disabled = True)]]

# 2 - the main window
window = sg.Window('Linear reductor gui', layout, grab_anywhere=True)
harden_window_active = False
hardened = False

# 3 - the event loop
i = 0
while True:
    event, values = window.read(timeout=100)
    #if event != sg.TIMEOUT_KEY:
        #print(i, event, values)
        
    
    if event in (None, 'Exit'):
        break
    i+=1
    if event == 'Find reductions':
        #window['-OUTPUT-'].update(read_sigma(values['-IN_SIGMA-'])[0])

        Sigma, interval_li = read_sigma(values['-IN_SIGMA-'])
        alpha = Fraction(values['-IN_ALPHA-'])
        beta = Fraction(values['-IN_BETA-'])
        epsilon = float(values["-IN_EPSILON-"])
        d = int(values["-IN_D-"])
        delta = int(values["-IN_DELTA-"])

        do_split = False
        split_count = 40

        var_stack = (d, delta, beta, alpha, epsilon, Sigma)

        interval_df, neighborhoods, intervals, interval_count = run_reductor(var_stack, interval_li, do_split, split_count)
        if interval_df is not None:
            window['-OUTPUT-'].update(interval_df)
        else:
            window['-HARDEN-'].update(disabled=False)

    if event == '-HARDEN-' and not harden_window_active:     # only run if not already showing a window2
        harden_window_active = True
        disallowed_cases = []
        # window 2 layout - note - must be "new" every time a window is created
        layout2 = [[sg.Text('Select cases that will not be used in the solution')]]
        for index, row in neighborhoods.iterrows():
            combination = row["combination"]
            wcolor, bcolor = "orange red", "orange red"
            if row["W"]: wcolor = "green"
            if row["B"]: bcolor = "green"
            layout2.append([sg.Text(f"{combination}"),
                sg.Button('W', key=f"W_{index}", button_color=("white", wcolor), disabled = not row["W"]),
                sg.Button('B', key=f"B_{index}", button_color=("white", bcolor), disabled = not row["B"])])
        layout2.append([sg.Text("Disallowed cases:"), sg.Output(key = '-HARDENED_CASES-', size=(30,3))])
        layout2.append([sg.Button("Find reductions", key="reduce2")])
        
        window_harden = sg.Window('Window 2', layout2, grab_anywhere=True, finalize=True)
        window_harden.move(window.current_location()[0]+500, window.current_location()[1])
    if harden_window_active:
        event, values = window_harden.read(timeout=0)
        # print("win2 ", event)
        #if event != sg.TIMEOUT_KEY:
            #print("harden_window ", event)
        
        if event[0:2] == "W_" or event[0:2] ==  "B_":
            button = window_harden[event]
            if event in disallowed_cases:
                disallowed_cases.remove(event)
                button.update(button_color = ("white", "green"))
            else:
                disallowed_cases.append(event)
                button.update(button_color = ("white", "red"))
            window_harden["-HARDENED_CASES-"].update(disallowed_cases)
        
        if event == "reduce2":
            harden_window_active = False
            window_harden.close()

            window['-OUTPUT-'].update("Solving hardened problem")
            
            for change in disallowed_cases:
                index = int(change[2::])
                column = change[0]
                neighborhoods.at[index, column] = False

            
            interval_df, neighborhoods, intervals, interval_count = run_reductor(var_stack, interval_li, do_split, split_count, neighborhoods)
            if interval_df is not None:
                window['-OUTPUT-'].update(interval_df)
            else:
                window['-HARDEN-'].update(disabled=False)



        if event == 'Exit' or event is None:
            # print("Closing window 2", event)
            harden_window_active = False
            window_harden.close()
        if event == 'Show':
            sg.popup('You entered ', values['-IN-'])


# 4 - the close
window.close()