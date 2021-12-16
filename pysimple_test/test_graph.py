import PySimpleGUI as sg
import time
import math
import pystray
from PIL import Image, ImageDraw
from simple_pid import PID

from kettle_image import *
from accessories import *
from elements import *
from pumps import *
from valves import *
from temp import *
from volume import *
from timer import *
from menu import *
from flow_directions import *
from settings import *
from pid_settings import *

#sg.theme_previewer()
sg.theme('Dark2')   # Add a touch of color
w, h = sg.Window.get_screen_size()
pid = PID(pid_settings["Kp"],pid_settings["Ki"],pid_settings["Kd"],setpoint=pid_settings["setpoint"],output_limits=pid_settings["output_limits"],auto_mode=pid_settings["auto_mode"],proportional_on_measurement=pid_settings["proportional_on_measurement"])

sample_time = 200

menu = {}
timer = {}
temp = {}
volume = {}
volume_lev = {}
chillers = {}
elements = {}
pumps = {}
valves = {}
flows = {}

def everythingOff(graph):
    for p in a_pumps:
        graph.DeleteFigure(pumps[p])
    for e in a_elements:
        graph.DeleteFigure(elements[e])

def updatePumps(graph, p, event):
    if(event == "loop"):
        if(a_pumps[p]["status"] != "off" and a_pumps[p]["status"] != "non_op"):
            graph.DeleteFigure(pumps[p])
            if(a_pumps[p]["status"] == "on_1"):
                pumps[p] = graph.DrawImage(data=a_pumps[p]["options"]["on"]["2"], location=a_pumps[p]["location"])
                a_pumps[p]["status"] = "on_2"
            elif(a_pumps[p]["status"] == "on_2"):
                pumps[p] = graph.DrawImage(data=a_pumps[p]["options"]["on"]["1"], location=a_pumps[p]["location"])
                a_pumps[p]["status"] = "on_1"
    else:
        if(a_pumps[p]["status"] != "non_op"):
            graph.DeleteFigure(pumps[p]) 
            if(a_pumps[p]["status"] == "off"):
                pumps[p] = graph.DrawImage(data=a_pumps[p]["options"]["on"]["1"], location=a_pumps[p]["location"])
                a_pumps[p]["status"] = "on_1"
                # **** ------------------------------------ ****
                # **** ---- CODE TO UPDATE ACTUAL PUMP ---- ****
                # **** ------------------------------------ ****
            elif(a_pumps[p]["status"] == "non_op"):
                pumps[p] = graph.DrawImage(data=a_pumps[p]["options"]["non_op"], location=a_pumps[p]["location"])
            else:
                pumps[p] = graph.DrawImage(data=a_pumps[p]["options"]["off"], location=a_pumps[p]["location"])
                a_pumps[p]["status"] = "off"
                # **** ------------------------------------ ****
                # **** ---- CODE TO UPDATE ACTUAL PUMP ---- ****
                # **** ------------------------------------ ****
    updateFlow(graph, event)
    
def valveLogic(graph, v):
    if(v == "v_hlt"):
        if(a_valves[v]["status"] == "open" and a_valves["v_mt_1"]["status"] == "close"):
            return False
        elif(a_valves[v]["status"] == "open" and a_valves["v_mt_1"]["status"] == "open"):
            graph.DeleteFigure(valves["v_mt_1"])
            valves["v_mt_1"] = graph.DrawImage(data=a_valves["v_mt_1"]["options"]["open_no"], location=a_valves["v_mt_1"]["location"])
            a_valves["v_mt_1"]["status"] = "open_no"
            return True
        elif(a_valves[v]["status"] == "close" and a_valves["v_mt_1"]["status"] == "open_no"):
            graph.DeleteFigure(valves["v_mt_1"])
            valves["v_mt_1"] = graph.DrawImage(data=a_valves["v_mt_1"]["options"]["open"], location=a_valves["v_mt_1"]["location"])
            a_valves["v_mt_1"]["status"] = "open"
            return True
        else:
            return True
    elif(v == "v_mt_1"):
        if(a_valves[v]["status"] == "open" and a_valves["v_hlt"]["status"] == "close"):
            return False
        elif(a_valves[v]["status"] == "open" and a_valves["v_hlt"]["status"] == "open"):
            graph.DeleteFigure(valves["v_hlt"])
            valves["v_hlt"] = graph.DrawImage(data=a_valves["v_hlt"]["options"]["open_no"], location=a_valves["v_hlt"]["location"])
            a_valves["v_hlt"]["status"] = "open_no"
            return True
        elif(a_valves[v]["status"] == "close" and a_valves["v_hlt"]["status"] == "open_no"):
            graph.DeleteFigure(valves["v_hlt"])
            valves["v_hlt"] = graph.DrawImage(data=a_valves["v_hlt"]["options"]["open"], location=a_valves["v_hlt"]["location"])
            a_valves["v_hlt"]["status"] = "open"
            return True
        else:
            return True
    else:
        return True
                
def updateValves(graph, v):
    status = a_valves[v]["status"]
    if(status != "open_no" and status != "close_no"):
        if(valveLogic(graph, v)):
            graph.DeleteFigure(valves[v])
            if(a_valves[v]["status"] == "close"):
                valves[v] = graph.DrawImage(data=a_valves[v]["options"]["open"], location=a_valves[v]["location"])
                a_valves[v]["status"] = "open"
                # **** ------------------------------------- ****
                # **** ---- CODE TO UPDATE ACTUAL VALVE ---- ****
                # **** ------------------------------------- ****
            elif(a_valves[v]["status"] == "open"):
                valves[v] = graph.DrawImage(data=a_valves[v]["options"]["close"], location=a_valves[v]["location"])
                a_valves[v]["status"] = "close" 
                # **** ------------------------------------- ****
                # **** ---- CODE TO UPDATE ACTUAL VALVE ---- ****
                # **** ------------------------------------- ****
            updateFlow(graph, "click")
        
def updateFlow(graph, event):
    for fd in flow_directions:
        status_logic = flow_directions[fd]["status"]["logic"]
        status_flow = flow_directions[fd]["status"]["flow"]
        if(status_flow != ""):
            if(status_flow == "flow_1"):
                status_flow_next = "flow_2"
            else:
                status_flow_next = "flow_1"
        else:
            status_flow_next = ""
        pump = flow_directions[fd]["pump"]
        status_pump = a_pumps[pump]["status"]
        if(event == "loop"):
            if(status_logic != "" and status_flow != ""):
                if(status_pump == "on_1" or status_pump == "on_2"):
                    graph.DeleteFigure(flows[fd])
                    flows[fd] = graph.DrawImage(data=flow_directions[fd]["logic"][status_logic][status_flow_next], location=(0,768))
                    flow_directions[fd]["status"]["flow"] = status_flow_next
        else:
            status_logic = ""
            status_flow = ""
            graph.DeleteFigure(flows[fd])
            if(status_pump == "on_1" or status_pump == "on_2"):
                #print("pump is on: {0}".format(fd))
                v_1 = flow_directions[fd]["valve_1"]
                v_2 = flow_directions[fd]["valve_2"]
                v_3 = flow_directions[fd]["valve_3"]
                v_1_status = a_valves[v_1]["status"]
                if(v_1_status == "open_no"):
                    v_1_status = "open"
                elif(v_1_status == "close_no"):
                    v_1_status = "close"
                if(v_2 != ""):
                    v_2_status = a_valves[v_2]["status"]
                    if(v_2_status == "open_no"):
                        v_2_status = "open"
                    elif(v_2_status == "close_no"):
                        v_2_status = "close"
                else:
                    v_2_status = ""
                if(v_3 != ""):
                    v_3_status = a_valves[v_3]["status"]
                    if(v_3_status == "open_no"):
                        v_3_status = "open"
                    elif(v_3_status == "close_no"):
                        v_3_status = "close"
                else:
                    v_3_status = ""
                for fl in flow_directions[fd]["logic"]:
                    #print("flow: {0}".format(fl))
                    #print("logic_1: " + v_1_status + " vs. " + flow_directions[fd]["logic"][fl]["valve_1"] + " logic_2: " + v_2_status + " vs. " + flow_directions[fd]["logic"][fl]["valve_2"] + " logic_3: " + v_3_status + " vs. " + flow_directions[fd]["logic"][fl]["valve_3"])
                    if(v_1_status == flow_directions[fd]["logic"][fl]["valve_1"]):
                        if(flow_directions[fd]["logic"][fl]["valve_2"] != ""):
                            if(flow_directions[fd]["logic"][fl]["valve_2"] == v_2_status):
                                if(flow_directions[fd]["logic"][fl]["valve_3"] != ""):
                                    if(flow_directions[fd]["logic"][fl]["valve_3"] == v_3_status):
                                        status_logic = fl
                                        status_flow = "flow_1"
                                else:
                                    status_logic = fl
                                    status_flow = "flow_1"
                        else:
                            if(flow_directions[fd]["logic"][fl]["valve_3"] == v_3_status):
                                status_logic = fl
                                status_flow = "flow_1"
            else:
                status_logic = ""
                status_flow = ""
                
            flow_directions[fd]["status"]["logic"] = status_logic
            flow_directions[fd]["status"]["flow"] = status_flow
            if(status_logic != "" and status_flow != ""):
                flows[fd] = graph.DrawImage(data=flow_directions[fd]["logic"][status_logic][status_flow], location=(0,768))
            else:
                if(status_pump == "on_1" or status_pump == "on_2"):
                    updatePumps(graph, pump, "click")
                flows[fd] = graph.DrawImage(data="", location=(0,768))

def tempInputUpdate(t):
    mt1_status = a_temp["mt_1"]["status"]
    mt2_status = a_temp["mt_2"]["status"]
    hlt_status = a_temp["hlt"]["status"]
    if t == "hlt":
        a_temp["mt_1"]["status"] = "off"
        a_temp["mt_2"]["status"] = "off"
    elif t == "mt_1":
        a_temp["hlt"]["status"] = "off"
        a_temp["mt_2"]["status"] = "off"
    elif t == "mt_2":
        a_temp["hlt"]["status"] = "off"
        a_temp["mt_1"]["status"] = "off"

def tempInput(graph, t):
    name = a_temp[t]["name"]
    target = a_temp[t]["target"]
    temp_target = target
    if a_temp[t]["status"] == "on":
        t_btn = toggle_btn_on
        status = "on"
        temp_status = "on"
        btn_status = True
    else:
        t_btn = toggle_btn_off
        status = "off"
        temp_status = "off"
        btn_status = False
        
    msg = ""
    
    mt1_status = a_temp["mt_1"]["status"]
    mt2_status = a_temp["mt_2"]["status"]
    hlt_status = a_temp["hlt"]["status"]
    if t == "hlt":
        if mt1_status == "on":
            msg = "HLT elements are currently driven by MT 1 target temp, changes will override this configuration!"
        elif mt2_status == "on":
            msg = "HLT elements are currently driven by MT 2 target temp, changes will override this configuration!"
    elif t == "mt_1":
        if hlt_status == "on":
            msg = "HLT elements are currently driven by HLT target temp, changes will override this configuration!"
        elif mt2_status == "on":
            msg = "HLT elements are currently driven by MT 2 target temp, changes will override this configuration!"
        else:
            msg = "Please be aware that target temp for MT 1 will control HLT elements!"
    elif t == "mt_2":
        if hlt_status == "on":
            msg = "HLT elements are currently driven by HLT target temp, changes will override this configuration!"
        elif mt1_status == "on":
            msg = "HLT elements are currently driven by MT 1 target temp, changes will override this configuration!"
        else:
            msg = "Please be aware that target temp for MT 2 will control HLT elements!"
    
    layout_temp = [
        [sg.Text(msg)],
        [sg.Slider(range=(0,212),default_value=target,size=(20,15),orientation="horizontal",font=("sans-serif", 12), key="slider"), sg.Graph(canvas_size=(50,35),graph_bottom_left=(0,0),graph_top_right=(50,35), key="graph_btn", enable_events=True)],
        [sg.T('')],
        [sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_save", enable_events=True), sg.Text(' '), sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_cancel", enable_events=True)]
    ]
    
    window_temp = sg.Window('Target Temp: {}'.format(name), layout_temp, finalize=True)
    graph_btn = window_temp.Element("graph_btn")
    graph_btn_save = window_temp.Element("graph_btn_save")
    graph_btn_cancel = window_temp.Element("graph_btn_cancel")
    button = graph_btn.DrawImage(data=t_btn, location=(0,25))
    save = graph_btn_save.DrawImage(data=btn_save, location=(0,25))
    cancel = graph_btn_cancel.DrawImage(data=btn_cancel, location=(0,25))
    
    while True:
        event, values = window_temp.read()
        if event == sg.WIN_CLOSED or event == 'graph_btn_cancel': # if user closes window or clicks cancel
            break
        elif event == 'graph_btn':
            graph_btn.DeleteFigure(button)
            if btn_status == True:
                btn_status = False
                temp_status = "off"
                button = graph_btn.DrawImage(data=toggle_btn_off, location=(0,25))
            else:
                btn_status = True
                temp_status = "on"
                button = graph_btn.DrawImage(data=toggle_btn_on, location=(0,25))
        elif event == 'graph_btn_save':
            print(a_elements["e_hlt_2"]["status"])
            temp_target = values["slider"]
            if temp_status != status:
                a_temp[t]["status"] = temp_status
                if temp_status == "on":
                    if t in ("hlt", "mt_1", "mt_2"):
                        tempInputUpdate(t)
                        
                if t in ("hlt", "mt_1", "mt_2"):
                    if a_elements["e_bk_2"]["status"] != "off":
                        if a_elements["e_hlt_1"]["status"] != "off":
                            updateElements(graph, "e_bk_2", "temp")
                            updateElements(graph, "e_hlt_1", "temp")
                    else:
                        if a_elements["e_hlt_1"]["status"] != "off":
                            updateElements(graph, "e_hlt_1", "temp")
                        if a_elements["e_hlt_2"]["status"] != "off":
                            updateElements(graph, "e_hlt_2", "temp")
                else:
                    print(a_elements["e_hlt_2"]["status"])
                    if a_elements["e_hlt_2"]["status"] != "off":
                        print("hlt_2 is on")
                        if a_elements["e_bk_1"]["status"] != "off":
                            a_elements["e_bk_1"]["status"] = "off"
                            updateElements(graph, "e_hlt_2", "temp")
                            updateElements(graph, "e_bk_1", "temp")
                    else:
                        if a_elements["e_bk_1"]["status"] != "off":
                            updateElements(graph, "e_bk_1", "temp")
                        if a_elements["e_bk_2"]["status"] != "off":
                            updateElements(graph, "e_bk_2", "temp")
            if temp_target != target:
                a_temp[t]["target"] = temp_target
            break

    window_temp.close()
    
def timerInput(graph, t):    
    msg = ""
    
    layout_timer = [
        [sg.Text(msg)],
        [sg.Slider(range=(0,24),default_value=a_timer[t]["hours"],size=(15,20),orientation="vertical",font=("sans-serif", 12), key="hours"), sg.Text(' '), sg.Slider(range=(0,59),default_value=a_timer[t]["minutes"],size=(15,20),orientation="vertical",font=("sans-serif", 12), key="minutes"), sg.Text(' '),sg.Slider(range=(0,59),default_value=a_timer[t]["seconds"],size=(15,20),orientation="vertical",font=("sans-serif", 12), key="seconds")],
        [sg.T('')],
        [sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_start", enable_events=True), sg.Text(' '), sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_stop", enable_events=True), sg.Text(' '), sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_clear", enable_events=True)]
    ]
    
    window_timer = sg.Window("Timer Input", layout_timer, finalize=True)
    graph_btn_start = window_timer.Element("graph_btn_start")
    graph_btn_stop = window_timer.Element("graph_btn_stop")
    graph_btn_clear = window_timer.Element("graph_btn_clear")
    start = graph_btn_start.DrawImage(data=btn_start, location=(0,25))
    stop = graph_btn_stop.DrawImage(data=btn_stop, location=(0,25))
    clear = graph_btn_clear.DrawImage(data=btn_clear, location=(0,25))
    
    while True:
        event, values = window_timer.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        elif event == 'graph_btn_clear':
            adjustTimerInput(0, 0, 0, 0, "off")
            updateTimer(graph, 0, "clear")
            break
        elif event == 'graph_btn_stop':
            current_time = time_as_int() - a_timer["timer"]["start_time"]
            timer_time = (a_timer["timer"]["hours"] * 60 * 60) + (a_timer["timer"]["minutes"] * 60) + a_timer["timer"]["seconds"]
            time_left = int(timer_time - current_time)
            adjustTimerInput(a_timer["timer"]["start_time"], time_left // 3600, ((time_left - ((time_left // 3600) * 60 * 60)) // 60), (time_left - (((time_left // 3600) * 60 * 60) + ((time_left - ((time_left // 3600) * 60 * 60)) // 60))) % 60, "off")
            updateTimer(graph, current_time, "stop")
            break
        elif event == 'graph_btn_start':
            if values["hours"] > 0 or values["minutes"] > 0 or values["seconds"] > 0:
                adjustTimerInput(time_as_int(), int(values["hours"]), int(values["minutes"]), int(values["seconds"]), "on")
            else:
                adjustTimerInput(0, 0, 0, 0, "off")
                updateTimer(graph, 0, "start")
            break

    window_timer.close()

def time_as_int():
    return int(round(time.time()))
    
def adjustTimerInput(start_time, hours, minutes, seconds, status):
    a_timer["timer"]["start_time"] = start_time
    a_timer["timer"]["hours"] = hours
    a_timer["timer"]["minutes"] = minutes
    a_timer["timer"]["seconds"] = seconds
    a_timer["timer"]["status"] = status
    
def updateTimer(graph, current_time, called):
    timer_time = (a_timer["timer"]["hours"] * 60 * 60) + (a_timer["timer"]["minutes"] * 60) + a_timer["timer"]["seconds"]
    if called != "stop":
        time_left = int(timer_time - current_time)
    else:
        time_left = timer_time
    hours = math.floor(time_left / 3600)
    minutes = (time_left - (hours * 3600)) // 60
    seconds = (time_left - ((hours * 3600) + (minutes * 60))) % 60
    if hours == 0 and minutes == 0 and seconds <= 10:
        t_color = a_timer["timer"]["options"]["secondary_color"]
        if seconds == 0:
            adjustTimerInput(0, 0, 0, 0, "off")
            t_color = a_timer["timer"]["options"]["color"]
    else:
        t_color = a_timer["timer"]["options"]["color"]
    graph.DeleteFigure(timer["timer"])
    timer["timer"] = graph.DrawText("{:02d}:{:02d}:{:02d}".format(hours,minutes, seconds), a_timer["timer"]["options"]["location"], font=(a_timer["timer"]["options"]["text"], a_timer["timer"]["options"]["size"]), color=t_color, text_location=sg.TEXT_LOCATION_CENTER)

def updateVolumeLev(graph, kettle):
    layers = int(math.floor(a_volume[kettle]["current_volume"] / a_volume[kettle]["gallons_layer"]))
    layer = 1
    x = 0
    y = a_volume[kettle]["layer_options"][1]["location"]["y"]
    for l in range(layers - 1):
        if layer <= 5:
            x = a_volume[kettle]["layer_options"][layer]["location"]["x"]
            i = a_volume[kettle]["layer_options"][layer]["image"]
            #print(y)
        volume_lev["{0}_{0}".format(kettle, layer)] = graph.DrawImage(data=i, location=(x,y))
        layer += 1
        y += 1

def updateElements(graph, e, event):
    if(event == "loop"):
        if(a_elements[e]["status"] != "off" and a_elements[e]["status"] != "non_op"):
            graph.DeleteFigure(elements[e])
            if(a_elements[e]["status"] == "on_1"):
                elements[e] = graph.DrawImage(data=a_elements[e]["options"]["on"]["2"], location=a_elements[e]["location"])
                a_elements[e]["status"] = "on_2"
            elif(a_elements[e]["status"] == "on_2"):
                elements[e] = graph.DrawImage(data=a_elements[e]["options"]["on"]["1"], location=a_elements[e]["location"])
                a_elements[e]["status"] = "on_1"
    else:
        # check to make sure only two elements on at the same time
        check = 0
        for ch in a_elements:
            if(a_elements[ch]["status"] == "on_1" or a_elements[ch]["status"] == "on_2"):
                check += 1
        if(check <= 2):
            if(a_elements[e]["status"] != "non_op"):
                graph.DeleteFigure(elements[e]) 
                if(a_elements[e]["status"] == "off"):
                    # **** --------------------------------------- ****
                    # **** ---- CODE TO UPDATE ACTUAL ELEMENT ---- ****
                    # **** --------------------------------------- ****
                    elements[e] = graph.DrawImage(data=a_elements[e]["options"]["on"]["1"], location=a_elements[e]["location"])
                    a_elements[e]["status"] = "on_1"
                else:
                    # **** --------------------------------------- ****
                    # **** ---- CODE TO UPDATE ACTUAL ELEMENT ---- ****
                    # **** --------------------------------------- ****
                    elements[e] = graph.DrawImage(data=a_elements[e]["options"]["off"], location=a_elements[e]["location"])
                    a_elements[e]["status"] = "off"
             
            check = 0
            for ch in a_elements:
                if(a_elements[ch]["status"] == "on_1" or a_elements[ch]["status"] == "on_2"):
                    check += 1
            if(check == 2):
                for ch in a_elements:
                    if(a_elements[ch]["status"] == "off"):
                        a_elements[ch]["status"] = "non_op"
                        graph.DeleteFigure(elements[ch])
                        elements[ch] = graph.DrawImage(data=a_elements[ch]["options"]["non_op"], location=a_elements[ch]["location"])
            else:
                for ch in a_elements:
                    if(a_elements[ch]["status"] == "non_op"):
                        a_elements[ch]["status"] = "off"
                        graph.DeleteFigure(elements[ch])
                        elements[ch] = graph.DrawImage(data=a_elements[ch]["options"]["off"], location=a_elements[ch]["location"])

def autoPIDLogic(graph, t):
    # find out which elements are on
    elem = {"1": False, "2": False}
    for e in a_temp[t]["elements"]:
        if a_elements[a_temp[t]["elements"][e]]["status"] != "off":
            elem[e] = True
    if elem["1"] and elem["2"]:
        Kp = a_temp[t]["pid"]["both"]["Kp"]
        Ki = a_temp[t]["pid"]["both"]["Ki"]
        Kd = a_temp[t]["pid"]["both"]["Kd"]
    elif elem["1"]:
        Kp = a_temp[t]["pid"]["1"]["Kp"]
        Ki = a_temp[t]["pid"]["1"]["Ki"]
        Kd = a_temp[t]["pid"]["1"]["Kd"]
        updateElements(graph, a_temp[t]["elements"]["2"], "click")
    elif elem["2"]:
        Kp = a_temp[t]["pid"]["2"]["Kp"]
        Ki = a_temp[t]["pid"]["2"]["Ki"]
        Kd = a_temp[t]["pid"]["2"]["Kd"]
        updateElements(graph, a_temp[t]["elements"]["1"], "click")
    else:
        Kp = a_temp[t]["pid"]["both"]["Kp"]
        Ki = a_temp[t]["pid"]["both"]["Ki"]
        Kd = a_temp[t]["pid"]["both"]["Kd"]
        updateElements(graph, a_temp[t]["elements"]["1"], "click")
        updateElements(graph, a_temp[t]["elements"]["2"], "click")
    pid.tunings = (Kp, Ki, Kd)
    pid.setpoint = a_temp[t]["target"]
    current_value = a_temp[t]["temp"]
    output = int(round(pid(current_value)))
    #print(output)
    # **** --------------------------------------- ****
    # **** ---- CODE TO UPDATE ACTUAL ELEMENT ---- ****
    # **** --------------------------------------- ****

def scheduleInput():    
    msg = "Nothing is currently scheduled. Please create a new schedule."
    
    time_layout = [
        
    ]
    
    col_1 = [
        [sg.CalendarButton('Calendar', pad=None, font=('sans-serif', 12, 'bold'), button_color=('green', 'white'), key='_CALENDAR_', format=('%d %B, %Y'))],
        [sg.T('')],
        [sg.Radio('AM', "AMPM", font=("sans-serif", 12), default=True), sg.Radio('PM', "AMPM", font=("sans-serif", 12))],
        [sg.Slider(range=(0,12),default_value=0,size=(30,20),orientation="horizontal",font=("sans-serif", 12), key="hours")],
        [sg.Text("Hour", font=("sans-serif", 12))],
        [sg.Slider(range=(0,59),default_value=0,size=(30,20),orientation="horizontal",font=("sans-serif", 12), key="minutes")],
        [sg.Text("Minutes", font=("sans-serif", 12))],
        [sg.T('')],
        [sg.Combo(["Red Ale", "Lager", "Porter"]), sg.Text(" "), sg.FileBrowse()],
        [sg.Text("Select a recipe from the dropdown or upload a new one.", font=("sans-serif", 12))]
    ]
    
    col_2 = [
        [sg.Multiline('', size=(60,30))]
    ]
    
    layout_schedule = [
        [sg.T('')],
        [sg.Text(msg, font=("sans-serif", 12))],
        [sg.T('')],
        [sg.Column(col_1), sg.VerticalSeparator(pad=(0,0)), sg.Column(col_2)],
        [sg.T('')],
        [sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_save", enable_events=True), sg.Text(' '), sg.Graph(canvas_size=(50,25),graph_bottom_left=(0,0),graph_top_right=(50,25), key="graph_btn_cancel", enable_events=True)]
    ]
    
    window_schedule = sg.Window("Schedule Input", layout_schedule, finalize=True)
    graph_btn_save = window_schedule.Element("graph_btn_save")
    graph_btn_cancel = window_schedule.Element("graph_btn_cancel")
    save = graph_btn_save.DrawImage(data=btn_save, location=(0,25))
    cancel = graph_btn_cancel.DrawImage(data=btn_cancel, location=(0,25))
    
    while True:
        event, values = window_schedule.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        #print(event)
        #print(values)
#         elif event in ('graph_btn_save', 'graph_btn_cancel'):
#             print(values)
#         elif event == "_CALENDAR_":
#             print(values)

    window_schedule.close()

def updateMenu(graph, m, event):
    if(event != "loop"):
        for i in a_menu:
            graph.DeleteFigure(menu[i])
        if(a_menu["menu"]["status"] == "open"):
#             graph(background_color="#2b2a2a")
            for i in a_menu:  
                menu[i] = graph.DrawImage(data=a_menu[i]["options"]["close"], location=a_menu[i]["location"])
                a_menu[i]["status"] = "close"
        else:
#             graph(background_color='#404040')
            for i in a_menu:
                menu[i] = graph.DrawImage(data=a_menu[i]["options"]["open"], location=a_menu[i]["location"])
                a_menu["menu"]["status"] = "open"
            if m == "schedule":
                scheduleInput()

class mainMenu():

    # All the stuff inside your window.
    #layout = [  [sg.Graph(canvas_size=(1366,768),graph_bottom_left=(0,0),graph_top_right=(1366,768),key="graph", enable_events=True)] ]
    ###########################
    #importlayout = [  [sg.Graph(canvas_size=(w,h),graph_bottom_left=(0,0),graph_top_right=(w,h),key="graph", enable_events=True)] ]
    layout = [  [sg.Graph(canvas_size=(1280,800),graph_bottom_left=(0,0),graph_top_right=(1280,800),key="graph", enable_events=True)] ]
    
    # Create the Window
    window = sg.Window('Brewery UI', layout, finalize=True)
    graph = window.Element("graph")
    
    for val in a_menu:
        menu["{0}".format(val)] = graph.DrawImage(data=a_menu[val]["options"]["open"], location=(0,768))
        
    for val in a_volume:
        updateVolumeLev(graph, val)
    
    kettle_base = graph.DrawImage(data=kettles, location=(0,768))
    logo = graph.DrawImage(data=logo, location=(1109,55))
    
    for val in a_timer:
        timer["{0}".format(val)] = graph.DrawText("{:02d}:{:02d}:{:02d}".format(a_timer[val]["hours"],a_timer[val]["minutes"],a_timer[val]["seconds"]), a_timer[val]["options"]["location"], font=(a_timer[val]["options"]["text"], a_timer[val]["options"]["size"]), color=a_timer[val]["options"]["color"], text_location=sg.TEXT_LOCATION_CENTER)
    for val in a_temp:
        temp["{0}".format(val)] = graph.DrawText("{}{}F".format(a_temp[val]["temp"], u"\N{DEGREE SIGN}"), a_temp[val]["options"]["location"], font= (a_temp[val]["options"]["text"], a_temp[val]["options"]["size"]), color=a_temp[val]["options"]["color"], text_location=sg.TEXT_LOCATION_CENTER)
    for val in a_volume:
        if val != "mt":
            volume["{0}".format(val)] = graph.DrawText("{} Gal".format(a_volume[val]["current_volume"]), a_volume[val]["options"]["location"], font= (a_volume[val]["options"]["text"], a_volume[val]["options"]["size"]), color=a_volume[val]["options"]["color"], text_location=sg.TEXT_LOCATION_CENTER)
    for val in a_chiller:
        chillers["{0}".format(val)] = graph.DrawImage(data=a_chiller[val]["options"]["default"], location=a_chiller[val]["location"])
    for val in a_elements:
        elements["{0}".format(val)] = graph.DrawImage(data=a_elements[val]["options"]["off"], location=a_elements[val]["location"])
    for val in a_pumps:
        pumps["{0}".format(val)] = graph.DrawImage(data=a_pumps[val]["options"]["off"], location=a_pumps[val]["location"])
    for val in a_valves:
        valves["{0}".format(val)] = graph.DrawImage(data=a_valves[val]["options"]["open"], location=a_valves[val]["location"])
    for val in flow_directions:
        flows["{0}".format(val)] = graph.DrawImage(data="", location=(0,768))
    
    # Event Loop to process "events" and get the "values" of the inputs
    pid.sample_time = sample_time * 0.001
    window_close = 0
    while True:
        for e in elements:
            updateElements(graph, e, "loop")
        for p in pumps:
            updatePumps(graph, p, "loop")
        for t in temp:
            if a_temp[t]["status"] == "on":
                autoPIDLogic(graph,t)
        event, values = window.read(sample_time)
        if a_timer["timer"]["status"] == "on":
            current_time = time_as_int() - a_timer["timer"]["start_time"]
            updateTimer(graph,current_time, "update")
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window_close = 1
        if event == 'graph':
            selected = graph.GetFiguresAtLocation(values['graph'])
            for s in selected: 
                for m in menu:
                    if(m != "background" and m != "line_1" and m != "line_2" and m != "line_3"):
                        if(m == "close" and menu[m] == s):
                            window_close = 1
                        elif(menu[m] == s):
                            updateMenu(graph, m, "click")
                if window_close < 1:
                    for tmr in timer:
                        if(timer[tmr] == s):
                            timerInput(graph,tmr)
                    for t in temp:
                        if(temp[t] == s):
                            tempInput(graph,t)
                    for e in elements:
                        if(elements[e] == s):
                            updateElements(graph, e, "click")
                    for p in pumps:
                        if(pumps[p] == s):
                            updatePumps(graph, p, "click")
                    for v in valves:
                        if(valves[v] == s):
                            updateValves(graph, v)
        if window_close:
            everythingOff(graph)
            break
    window.close()        
        
if __name__ == "__main__":
    mainMenu()