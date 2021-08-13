import logging
from fractions import Fraction

import PySimpleGUI as sg

from pathlib import Path
import os

from base_logger import logger
from main import run_reductor
from solver import find_reductions
from problem import Problem

def solve_problem(problem = None, disallowed_cases = None):
    # This changes if disallowed cases are passed
    neighborhoods = None

    # If no problem is given, read inputs and create that problem
    if problem is None:
        Sigma_string = values['-IN_SIGMA-']
        alpha = Fraction(values['-IN_ALPHA-'])
        beta = Fraction(values['-IN_BETA-'])
        epsilon = float(values["-IN_EPSILON-"])
        d = int(values["-IN_D-"])
        delta = int(values["-IN_DELTA-"])

        do_split = bool(values["-IN_DO_SPLITS-"])
        split_count = int(values["-IN_SPLIT_COUNT-"])

        problem = Problem(d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon)
    
    # Disallowed cases can only be passed if the problem is also passed.
    elif disallowed_cases is not None:
        neighborhoods = problem.solution["neighborhoods"] 
    
        for change in disallowed_cases:
            index = int(change[2::])
            column = change[0]
            neighborhoods.at[index, column] = False


    problem, output_string = run_reductor(problem, neighborhoods)
    
    window['-OUTPUT-'].update(output_string)

    # After the first call a problem exists, enable hardening at that point
    window['-HARDEN-'].update(disabled=False)

    # Set the save directory to the one indicated by the problem type (in an OS-independent way)
    main_dir = Path(__file__).parent.parent / "problems"
    global save_path
    if problem.parameters["alpha"] < problem.parameters["beta"] and (main_dir / "slack").is_dir():
        save_path = main_dir / "slack"

    elif problem.parameters["alpha"] > problem.parameters["beta"] and (main_dir / "anti-slack").is_dir():
        save_path = main_dir / "anti-slack"

    elif (main_dir / "exact").is_dir():
        save_path = main_dir / "exact"
    
    # Refresh the saving path info box
    update_save_path_view()
    return problem

def update_save_path_view(savename = "Unnamed problem"):
    if savename == "":
        window["-PATH_OUTPUT-"].update("Problem name cannot be empty!")
    else:
        filename = "".join(x for x in list(savename.replace(" ", "_")) if x.isalnum() or x=="_").lower()
        md_path = save_path / filename / f"{filename}.md"
        pickle_path = save_path / filename / f"{filename}.pickle"
        txt = f"Saving will create the following files: \n{md_path}\n{pickle_path}\nAnything that wasn't stored after ## Notes in the markdown file will be lost."
        window["-PATH_OUTPUT-"].update(txt)

        

## Run GUI

sg.theme("DarkBlue") # Add some color

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


# A good startingpoint for savepath should be the root of linear reductor
save_path = Path(__file__).parent.parent

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
        [sg.Multiline(size=(100, 4), key="-PATH_OUTPUT-")],
        [sg.Input(key="-IN_SAVEFOLDER_FIX-", enable_events = True, visible=False), sg.FolderBrowse('Browse save location', key="-IN_SAVEFOLDER-", target="-IN_SAVEFOLDER_FIX-", initial_folder = save_path), sg.Button("Save", key="-SAVE-", size=(15,1), disabled=True)]]

# 2 - the main window
window = sg.Window('Linear reductor gui', layout, grab_anywhere=True)


harden_window_active = False
hardened = False


# 3 - the event loop

while True:
    event, values = window.read(timeout=100)

    if event in (None, 'Exit'):
        break

    if event == 'Find reductions':
        # Try to solve problem. Problem-class object with possible solutions is returned.
        problem = solve_problem()

    if event == '-HARDEN-' and not harden_window_active:     # only run if not already showing a window2
        harden_window_active = True
        disallowed_cases = []
        # window 2 layout - note - must be "new" every time a window is created
        layout2 = [[sg.Text('Select cases that will not be used in the solution')]]
        table_layout = []
        for index, row in problem.solution["neighborhoods"].iterrows():
            combination = row["combination"]
            wcolor, bcolor = "orange red", "orange red"
            if row["W"]: wcolor = "green"
            if row["B"]: bcolor = "green"
            table_layout.append([sg.Text(f"{combination}", size=(20, 1)),
                sg.Button('W', key=f"W_{index}", button_color=("white", wcolor), disabled = not row["W"]),
                sg.Button('B', key=f"B_{index}", button_color=("white", bcolor), disabled = not row["B"])])
        
        table_height = min(400, 40*problem.solution["neighborhoods"].shape[0])
        layout2.append([sg.Column(table_layout, scrollable = True, vertical_scroll_only = True, expand_x = True, size=(200, table_height))])
        layout2.append([sg.Text("Disallowed cases:"), sg.Multiline(key = '-HARDENED_CASES-', size=(30,3))])
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
        update_save_path_view(values['-IN_NAME-'])

    if event == "-IN_NAME-":
        # Don't allow saving without modifying the name first
        window["-SAVE-"].update(disabled=False)
        update_save_path_view(values['-IN_NAME-'])
    
    if event == "-SAVE-":
        saved, error_code = problem.save(save_path, values['-IN_NAME-'])
        if saved:
            window["-PATH_OUTPUT-"].update("Problem saved succesfully!")
        else: 
            window["-PATH_OUTPUT-"].update("Saving failed!", error_code)

    if harden_window_active:
        event, values = window_harden.read(timeout=0)
        
        if event == '-CANCEL-' or event is None:
            # print("Closing window 2", event)
            harden_window_active = False
            window_harden.close()
        
        elif event[0:2] == "W_" or event[0:2] ==  "B_":
            button = window_harden[event]
            if event in disallowed_cases:
                disallowed_cases.remove(event)
                button.update(button_color = ("white", "green"))
            else:
                disallowed_cases.append(event)
                button.update(button_color = ("white", "red"))
            window_harden["-HARDENED_CASES-"].update(disallowed_cases)
        
        if event == "-REDUCE-":
            # Update the problem with made changes and try to solve it
            window['-OUTPUT-'].update("Solving hardened problem")
            problem = solve_problem(problem, disallowed_cases)
            harden_window_active = False
            window_harden.close()


            


# 4 - the close
window.close()
