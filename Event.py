class Event:

    def __init__(self, event_sku, prog_type, driver_duration, auton_duration, division_names):
        self.event_sku = event_sku
        self.prog_type = prog_type
        self.driver_duration = driver_duration
        self.auton_duration = auton_duration
        self.division_names = division_names
        self.matches = None

    def __str__(self):
        s = f"{self.prog_type}: {self.event_sku}"
        if len(self.division_names) <= 0:
            s += "\n\t No divisions"
        else:
            for name in self.division_names:
                s += f"\n\t{name}"
        return s

    def has_auton(self):
        return self.auton_duration > 0

def event_templates(prog_type, driver_duration, auton_duration):
    def event(event_sku, division_names):
        return Event(
            event_sku=event_sku,
            prog_type=prog_type,
            driver_duration=driver_duration,
            auton_duration=auton_duration,
            division_names=division_names,
        )
    return event

_V5RC = event_templates(
    prog_type="V5RC",
    driver_duration=105,
    auton_duration=15,
)

_VURC = event_templates(
    prog_type="VURC",
    driver_duration=75,
    auton_duration=45,
)

_VIQRC = event_templates(
    prog_type="VIQRC",
    driver_duration=60,
    auton_duration=0,
)