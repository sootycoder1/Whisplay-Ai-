import system_controller_STAGE12010_DEV_MIC_STAGE420_LOCKED as stage420


class OneTurnController(stage420.SystemController):

    def heartbeat(self):
        pass

    def monitor_runtime(self):
        pass

    def get_input(self):
        return "check system status"


    def output(self, response):
        print("[ACTUAL LOOP OUTPUT]", response.get("response"))
        stage420.STATE["running"] = False

    def remember_turn(self, text, response):
        print("[ACTUAL LOOP MEMORY]", text)

    def shutdown(self):
        print("[ACTUAL LOOP SHUTDOWN]")


original_dry_run = stage420.action_router.STATE["dry_run"]
stage420.action_router.STATE["dry_run"] = False
stage420.STATE["running"] = True

try:
    controller = OneTurnController()
    controller.run()

    result = stage420.STATE.get("last_action_result", {})

    assert result.get("ok") is True, result
    assert result.get("tool") == "system_status", result
    assert result.get("result", {}).get("action") == "system_status", result
    assert stage420.STATE.get("last_response", {}).get("response") == "Whisplay runtime status requested.", stage420.STATE.get("last_response")

    print("STAGE420_ACTUAL_ONE_TURN_PASS")

finally:
    stage420.action_router.STATE["dry_run"] = original_dry_run
    stage420.STATE["running"] = False
