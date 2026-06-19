import system_controller_STAGE12010_DEV_MIC as sc

# Ensure runtime loop runs
sc.STATE["running"] = True

controller = sc.SystemController()
controller.load_subsystems()
controller.run()
