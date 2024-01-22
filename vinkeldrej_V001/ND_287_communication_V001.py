from vinkeldrej_V001 import ND_287
import time

class Heidenhain_display():
    """
    I denne Class kan du via pc styre HEIDENHAIN ND-278.
    COM-porten skal koden nok selv finde så længe
    USB-forbindelsen er sat op korrekt
    
    ND.lock_keyboard()
    ND.open_keyboard()
    ND.request_data("A0000") #ID
    ND.request_data("A0100") #disp val
    ND.request_data("A0200") #position
    ND.request_data("A0400") #soft ID
    ND.request_data("A0800") #status bar
    ND.request_data("A0900") #status indicators
    ND.print_ND()
    ND.set_to_zero()
    """

    ND=ND_287()

    ND.print_ND()
    ND.set_to_zero()
    time.sleep(3)
    ND.print_ND()
    time.sleep(3)
    ND.print_ND()