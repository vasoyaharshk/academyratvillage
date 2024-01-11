from queue import Queue


tags = Queue()  # de thread arduino a main
reload_canvas = Queue()  # de thread rt_plots a gui
update_plots = Queue()  # de gui a rt_plots
trials = Queue()  # de thread bpod a main
responses = Queue()  # de thread touch a main o thread bpod
softcodes = Queue(maxsize=3)  # de softcode_handler a main o thread bpod
