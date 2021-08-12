import logging
from fractions import Fraction

import PySimpleGUI as sg

from base_logger import logger
from main import run_reductor
from solver import find_reductions
from problem import Problem

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

# Disable all logs at start, as default value for logging level is OFF
logging.disable()

logger.addHandler(ch)



# 1- the layout
layout = [[sg.Text('Sigma:', size=(15,1)), sg.Input(key='-IN_SIGMA-', size=(32,1), default_text="[0, 1/3) U (1/3, 1]")],
          [sg.Text('(Alpha) Active >=', size=(15,1)), sg.Input(key='-IN_ALPHA-', size=(32,1), default_text="1")],
          [sg.Text('(Beta) Passive <=', size=(15,1)), sg.Input(key='-IN_BETA-', size=(32,1), default_text="1")],
          [sg.Text('epsilon', size=(15,1)), sg.Input(key='-IN_EPSILON-', default_text=0.0001, size=(32,1))],
          [sg.Text('d, delta:', size=(15,1)), sg.Input(key='-IN_D-', size=(2,1), default_text=3), sg.Input(key='-IN_DELTA-', size=(2,1), default_text=3)],
          [sg.Checkbox("Make splits", key='-IN_DO_SPLITS-'), sg.Input(key='-IN_SPLIT_COUNT-', size=(4,1), default_text=6)],
          [sg.Button('Find reductions', size=(15,1)), sg.Button('Exit', size=(15,1)), sg.Text("Logging level"), sg.Combo(["OFF", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default_value="OFF", key = "-IN_DEBUG-", enable_events = True)],
          [sg.Multiline(size = (100,10), key = '-OUTPUT-')],
          [sg.Button("Harden problem", key = "-HARDEN-", size=(15,1), disabled = True)],
          [sg.Text("Enter problem name", size=(20,1)), sg.Input(key="-IN_NAME-", size=(32,1), default_text="Unnamed problem", enable_events=True)],
          [sg.Multiline(size=(100, 3), key="-PATH_OUTPUT-")],
          [sg.Input(key="-IN_SAVEFOLDER_FIX-", enable_events = True, visible=False), sg.FolderBrowse('Select save location', key="-IN_SAVEFOLDER-", target="-IN_SAVEFOLDER_FIX-"), sg.Button("Save", key="-SAVE-", size=(15,1), disabled=True)]]

# 2 - the main window
window = sg.Window('Linear reductor gui', layout, grab_anywhere=True)
harden_window_active = False
hardened = False
# Before allowing save, check that a folder and name are chosen
folder_chosen, name_chosen = False, False


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

        Sigma_string = values['-IN_SIGMA-']
        alpha = Fraction(values['-IN_ALPHA-'])
        beta = Fraction(values['-IN_BETA-'])
        epsilon = float(values["-IN_EPSILON-"])
        d = int(values["-IN_D-"])
        delta = int(values["-IN_DELTA-"])

        do_split = False
        split_count = 40

        problem = Problem(d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon)

        problem, output_string = run_reductor(problem)
        window['-OUTPUT-'].update(output_string)

        if problem.solution["interval_df"] is None:
            window['-HARDEN-'].update(disabled=False)

    if event == '-HARDEN-' and not harden_window_active:     # only run if not already showing a window2
        harden_window_active = True
        disallowed_cases = []
        # window 2 layout - note - must be "new" every time a window is created
        layout2 = [[sg.Text('Select cases that will not be used in the solution')]]
        for index, row in problem.solution["neighborhoods"].iterrows():
            combination = row["combination"]
            wcolor, bcolor = "orange red", "orange red"
            if row["W"]: wcolor = "green"
            if row["B"]: bcolor = "green"
            layout2.append([sg.Text(f"{combination}"),
                sg.Button('W', key=f"W_{index}", button_color=("white", wcolor), disabled = not row["W"]),
                sg.Button('B', key=f"B_{index}", button_color=("white", bcolor), disabled = not row["B"])])
        layout2.append([sg.Text("Disallowed cases:"), sg.Output(key = '-HARDENED_CASES-', size=(30,3))])
        layout2.append([sg.Button("Find reductions", key="-REDUCE-"), sg.Button("Cancel", key="-CANCEL-")])
        
        window_harden = sg.Window('Window 2', layout2, grab_anywhere=True, finalize=True)
        window_harden.move(window.current_location()[0]+500, window.current_location()[1])

    if event == "-IN_DEBUG-":
        mapper = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARNING, "ERROR":logging.ERROR, "CRITICAL":logging.CRITICAL}
        level = values["-IN_DEBUG-"]
        if level == "OFF":
            logging.disable()
        else:
            logging.disable(logging.NOTSET)
            logger.setLevel(mapper[level])
    
    if event == "-IN_SAVEFOLDER_FIX-":
        folder_chosen = True
        filename = "".join(x for x in list(values['-IN_NAME-'].replace(" ", "_")) if x.isalnum() or x=="_").lower()
        txt = f"Saving the following files: \n{values['-IN_SAVEFOLDER-']}/{filename}/{filename}.md \n{values['-IN_SAVEFOLDER-']}/{filename}/{filename}.json"
        window["-PATH_OUTPUT-"].update(txt)
        if folder_chosen and name_chosen:
            window["-SAVE-"].update(disabled=False)

    if event == "-IN_NAME-":
        name_chosen = True
        if values['-IN_NAME-'] == "":
            window["-PATH_OUTPUT-"].update("Problem name cannot be empty!")
        else:
            filename = "".join(x for x in list(values['-IN_NAME-'].replace(" ", "_")) if x.isalnum() or x=="_").lower()
            txt = f"Saving the following files: \n{values['-IN_SAVEFOLDER-']}/{filename}/{filename}.md \n{values['-IN_SAVEFOLDER-']}/{filename}/{filename}.json"
            window["-PATH_OUTPUT-"].update(txt)
        if folder_chosen and name_chosen:
            window["-SAVE-"].update(disabled=False)
    
    if event == "-SAVE-":
        if problem.save_to_dir(values['-IN_SAVEFOLDER-'], values['-IN_NAME-']):
            window["-PATH_OUTPUT-"].update("Problem saved!")

    if harden_window_active:
        event, values = window_harden.read(timeout=0)
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
        
        if event == "-REDUCE-":
            harden_window_active = False
            window_harden.close()

            window['-OUTPUT-'].update("Solving hardened problem")
            
            neighborhoods = problem.solution["neighborhoods"] 
            
            for change in disallowed_cases:
                index = int(change[2::])
                column = change[0]
                neighborhoods.at[index, column] = False

            
            problem, output_string = run_reductor(problem, neighborhoods)
            if problem.solution["interval_df"] is not None:
                window['-OUTPUT-'].update(output_string)
            else:
                window['-HARDEN-'].update(disabled=False)



        if event == '-CANCEL-' or event is None:
            # print("Closing window 2", event)
            harden_window_active = False
            window_harden.close()


# 4 - the close
window.close()
