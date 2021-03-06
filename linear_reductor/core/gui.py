import logging
from fractions import Fraction
import threading
import sys
import PySimpleGUI as sg
from tqdm import tqdm
import pandas as pd

import re
from pathlib import Path
import os

from base_logger import logger
from main import run_reductor, create_output
from solver import find_reductions
from problem import Problem, load_problem


# Function to start multiple solver threads, mainly for brute force solving.
def start_subprocesses(max_split, min_split=1):
    threads = [None]*(max_split-min_split+1)
    for split in range(min_split, max_split + 1):
        thread = threading.Thread(name = f"Solver {split}", target=solve_problem, args=(window, values), kwargs={"fix_splits": split}, daemon=True)
        threads[split-1] = thread
        # Create the threads, but as multiprocessing doesn't seem to help much, run them sequentially (also helps with debugs) 
    thread_df = pd.DataFrame({"Thread":threads, "Discretized":["-"]*(max_split-min_split+1), "Complete":[False]*(max_split-min_split+1), "Solution":[None]*(max_split-min_split+1)}, index = list(range(min_split, max_split + 1)))

    # window 3 layout - note - must be "new" every time a window is created
    layout3 = [[sg.Text('Reducing the problem with different split counts')],
    [sg.Multiline("solver situation", size = (50,20), key="-OUT_SOLVERS-")]]
    
    window_solver = sg.Window('Multiple split solver', layout3, grab_anywhere=True, finalize=True)
    
    # Start the first thread
    threads[0].start()
    return thread_df, window_solver

# Solver is run on a separate thread, as the GUI would otherwise freeze.
def solve_problem(window, values, problem = None, disallowed_cases = None, fix_splits=None):
    # This changes if disallowed cases are passed
    neighborhoods = None

    logger.debug("Starting a solver thread")

    # Tell about starting the progress
    if fix_splits is None:
        window.write_event_value('-PROGRESS-', " ")

    
    # If no problem is given, read inputs and create that problem
    if problem is None:
        Sigma_string = values['-IN_SIGMA-']
        alpha = Fraction(values['-IN_ALPHA-'])
        beta = Fraction(values['-IN_BETA-'])
        epsilon = float(values["-IN_EPSILON-"])
        d = int(values["-IN_D_DELTA-"])
        delta = int(values["-IN_D_DELTA-"])

        do_split = bool(values["-IN_DO_SPLITS-"])
        
        # Allow fixing split count for brute force try-all solution.
        if fix_splits is None:
            split_count = int(values["-IN_SPLIT_COUNT-"])
        else:
            split_count = fix_splits

        problem = Problem(d, delta, beta, alpha, Sigma_string, do_split, split_count, epsilon)
    
    # Disallowed cases can only be passed if the problem is also passed.
    elif disallowed_cases is not None:
        neighborhoods = problem.solution["neighborhoods"] 
    
        for change in disallowed_cases:
            index = int(change[2::])
            column = change[0]
            neighborhoods.at[index, column] = False

    problem, output_string = run_reductor(problem, neighborhoods, do_print=True)

    logger.debug("Solver thread is finished!")

    # If the thread was only one subthread in try-all situation, just tell that you're finished.
    if fix_splits is not None:
        window.write_event_value(f'-SUBPROGRESS_DONE_{fix_splits}-', problem)
        return

    
    window.write_event_value('-PROGRESS-', output_string)

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
    
    window.write_event_value('-PROGRESS_DONE-', problem)
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
        self.formatter = logging.Formatter('%(levelname)s: %(message)s')


    def emit(self, record):
        sg.Print(self.formatter.format(record))

ch = GuiHandler()

# Disable all logs at start, as default value for logging level is OFF
logging.disable()

logger.addHandler(ch)

# Redirect stderr to -OUTPUT- element. This will catch the progressbars made by tqdm, and will display any error messages.
class StdHandler:
    def __init__(self):
        pass

    def write(self, s):
        pro = re.search(r'(\d?\d?\d%)', str(s))
        if pro is not None:
            window["-PROGRESS-"].update(int(pro.group(0)[0:-1]))
        window["-OUTPUT-"].update(s)

    def flush(self):
        return

sys.stderr = StdHandler()

        

# A good startingpoint for savepath should be the root of linear reductor
save_path = Path(__file__).parent.parent

# 1- the layout
layout = [[sg.Text('Sigma:', size=(15,1)), sg.Input(key='-IN_SIGMA-', size=(32,1), default_text="[0, 1/3) U (1/3, 1]")],
        [sg.Text('(Alpha) Active >=', size=(15,1)), sg.Input(key='-IN_ALPHA-', size=(32,1), default_text="1")],
        [sg.Text('(Beta) Passive <=', size=(15,1)), sg.Input(key='-IN_BETA-', size=(32,1), default_text="1")],
        [sg.Text('epsilon', size=(15,1)), sg.Input(key='-IN_EPSILON-', default_text=0.0001, size=(32,1))],
        [sg.Text('d, delta:', size=(15,1)), sg.Input(key='-IN_D_DELTA-', size=(2,1), default_text=3)],
        [sg.Checkbox("Make splits", key='-IN_DO_SPLITS-', enable_events=True), sg.Input(key='-IN_SPLIT_COUNT-', size=(4,1), default_text=6)],
        [sg.Checkbox("Try all splits sequentially", key='-IN_TRY_ALL-', disabled = True, tooltip="Try all split values up to the input. This may take a long time!")],
        [sg.Button('Find reductions', key ="-REDUCE-", size=(15,1)), sg.Button("Load problem", key = "-LOAD-", size=(15,1)), sg.Button('Exit', size=(15,1)), sg.Text("Logging level"), sg.Combo(["OFF", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default_value="OFF", key = "-IN_DEBUG-", enable_events = True)],
        [sg.ProgressBar(100, key = "-PROGRESS-", orientation = "horizontal", size = (70, 10), visible = True)],
        [sg.Multiline(size = (100,10), key = '-OUTPUT-')],
        [sg.Button("Harden problem", key = "-HARDEN-", size=(15,1), disabled = False)],
        [sg.Text("Enter problem name", size=(20,1)), sg.Input(key="-IN_NAME-", size=(32,1), default_text="Unnamed problem", enable_events=True)],
        [sg.Multiline(size=(100, 4), key="-PATH_OUTPUT-")],
        [sg.Input(key="-IN_SAVEFOLDER_FIX-", enable_events = True, visible=False), sg.FolderBrowse('Browse save location', key="-IN_SAVEFOLDER-", target="-IN_SAVEFOLDER_FIX-", initial_folder = save_path), sg.Button("Save", key="-SAVE-", size=(15,1), disabled=True)]]

# 2 - the main window
window = sg.Window('Linear reductor gui', layout, grab_anywhere=True)

harden_window_active = False
hardened = False
thread = None
solving = False


# 3 - the event loop

while True:
    event, values = window.read(timeout=100)

    if event in (None, 'Exit'):
        break

    if event == '-REDUCE-':
        # Try to solve problem. Problem-class object with possible solutions is returned.
        
        if not solving:
            # If try-all checkbox is selected, all splits from 0 to chosen value are tried sequentially.
            if values["-IN_TRY_ALL-"]:
                thread_df, window_solver = start_subprocesses(int(values["-IN_SPLIT_COUNT-"]))

            else:
                thread = threading.Thread(name = "Solver", target=solve_problem, args=(window, values), daemon=True)
                thread.start()
            
            solving = True
            window["-REDUCE-"].update(disabled = True)
        

    if event == "-PROGRESS-":
        output = "Working on the problem...\n"+str(values["-PROGRESS-"])
        window['-OUTPUT-'].update(output)

    if event == '-PROGRESS_DONE-':
        if thread.is_alive():
            thread.join(0.25)
        solving = False
        problem = values["-PROGRESS_DONE-"]
        window['-HARDEN-'].update(disabled = False)
        window["-REDUCE-"].update(disabled = False)

    # Handle all finishing try-all subprocesses
    if "-SUBPROGRESS_DONE_" in event:
        # Extract the subprocess index
        split = int(event.split("_")[-1][0:-1])

        # Start the next thread, if it exists
        if thread_df.index[-1] > split:
            thread_df.loc[split+1, "Thread"].start()

        # Update the dataframe 
        thread = thread_df.at[split, "Thread"]
        
        solution = values[event].solution["interval_df"]
        thread_df.at[split, "Solution"] = solution
        if solution is None:
            thread_df.at[split, "Discretized"] = False
            thread_df.at[split, "Complete"] = True
        else:
            thread_df.at[split, "Discretized"] = True
            thread_df.at[split, "Complete"] = True
        
        
        s = thread_df.to_string(columns = ["Discretized", "Complete"])
        window_solver["-OUT_SOLVERS-"].update(s)
        
        if thread_df.loc[:, "Complete"].all():
            solving = False
            window['-HARDEN-'].update(disabled = False)
            window["-REDUCE-"].update(disabled = False)

            solutions = thread_df.loc[thread_df["Discretized"], :]
            window["-OUTPUT-"].update(f"All solvers have completed.\n")
            window["-OUTPUT-"].write(f"{solutions.shape[0]} solutions found in {thread_df.shape[0]} splits.\n")
            logger.debug(f"{solutions.shape[0]} solutions found in {thread_df.shape[0]} splits.")
            
            #if thread_df["Discretized"].any():
            #    window["-OUTPUT-"].write()
            
            window_solver.close()
        thread.join(0.25)
        


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
        layout2.append([sg.Button("Find reductions", key="-REDUCE_HARDENED-"), sg.Button("Cancel", key="-CANCEL-")])
        
        window_harden = sg.Window('Hardening window', layout2, grab_anywhere=True, finalize=True)
        window_harden.move(window.current_location()[0]+500, window.current_location()[1])

    if event == "-IN_DEBUG-":
        mapper = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARNING, "ERROR":logging.ERROR, "CRITICAL":logging.CRITICAL}
        level = values["-IN_DEBUG-"]
        if level == "OFF":
            logging.disable()
        else:
            logging.disable(logging.NOTSET)
            logger.setLevel(mapper[level])
    
    if event == "-IN_DO_SPLITS-":
        if values["-IN_DO_SPLITS-"]:
            window["-IN_TRY_ALL-"].update(disabled = False)
        else:
            window["-IN_TRY_ALL-"].update(value = False, disabled = True)
    
    if event == "-IN_SAVEFOLDER_FIX-":
        update_save_path_view(values['-IN_NAME-'])

    if event == "-IN_NAME-":
        # Don't allow saving without modifying the name first
        window["-SAVE-"].update(disabled=False)
        update_save_path_view(values['-IN_NAME-'])
    
    if event == "-LOAD-":
        load_input = sg.popup_get_file("Load a saved problem", file_types=(("Problem files", "*.pickle"),), initial_folder=Path(__file__).parent.parent / "problems")
        if load_input is not None:
            with open(load_input, "r") as f:
                p, message = load_problem(load_input)
                if p is None:
                    tqdm.write(message)
                    tqdm.write(f"No problem was found at the file in {load_input}. Exiting program.")
                elif not p.is_valid_problem():
                    tqdm.write(f"Problem was found, but it was corrupted. Exiting program.")
                else:
                    # Load problem
                    problem = p

                    # Unpack the problem definition
                    logger.debug("Loading problem definition.")
                    window['-IN_SIGMA-'].update(p.parameters["Sigma_string"])
                    window['-IN_ALPHA-'].update(p.parameters["alpha"])
                    window['-IN_BETA-'].update(p.parameters["beta"])
                    window['-IN_EPSILON-'].update(p.parameters["epsilon"])
                    window['-IN_D_DELTA-'].update(p.parameters["d"])
                    window['-IN_D_DELTA-'].update(p.parameters["delta"])
                    window['-IN_DO_SPLITS-'].update(p.parameters["do_split"])
                    window['-IN_SPLIT_COUNT-'].update(p.parameters["split_count"])
                    window['-OUTPUT-'].update("Problem loaded succesfully!\n")
                    logger.debug("Problem definition loaded.")

                    # Unpack the problem solution
                    try:
                        logger.debug("Loading problem solution.")
                        interval_df = p.solution["interval_df"]
                        neighborhoods = p.solution["neighborhoods"]
                        manual_neighborhoods = p.solution["manual_neighborhoods"]
                        var_stack, *_ = p.get_parameters()
                        output_string = create_output(interval_df, neighborhoods, var_stack, manual_neighborhoods)
                        window['-OUTPUT-'].write(output_string)
                        logger.debug("Problem solution loaded.")
                    
                    # No solution found
                    except Exception as e:
                        logger.debug(e)
                        window['-OUTPUT-'].write("No solution found!")
                    
                    # Set the save directory to the one indicated by the problem type (in an OS-independent way)
                    window['-IN_NAME-'].update(p.parameters["name"])
                    main_dir = Path(__file__).parent.parent / "problems"
                    if problem.parameters["alpha"] < problem.parameters["beta"] and (main_dir / "slack").is_dir():
                        save_path = main_dir / "slack"

                    elif problem.parameters["alpha"] > problem.parameters["beta"] and (main_dir / "anti-slack").is_dir():
                        save_path = main_dir / "anti-slack"

                    elif (main_dir / "exact").is_dir():
                        save_path = main_dir / "exact"
                    
                    # Refresh the saving path info box
                    update_save_path_view()

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
        
        if event == "-REDUCE_HARDENED-":
            # Update the problem with made changes and try to solve it
            window['-OUTPUT-'].update("Solving hardened problem")
            if not solving:
                thread = threading.Thread(name = "Solver", target=solve_problem, args=(window, values), kwargs={"problem":problem, "disallowed_cases":disallowed_cases}, daemon=True)
                thread.start()
                solving = True
            window["-REDUCE-"].update(disabled = True)
            harden_window_active = False
            window_harden.close()


            


# 4 - the close
window.close()

    