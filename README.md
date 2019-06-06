# Coupled Alarms

This component keeps all defined `alarm_control_panel`s in sync of their states.

* If you disarm one alarm in the group – others will disarm as well.
* If you trigger one alarm in the group – others will trigger as well.
* Et cetera...

## Installation

1. Clone this repo as `coupled_alarms` dir into $HA_CONFIG_DIR/custom_components/:
   ```
   $ cd custom_components
   $ git clone git@github.com:cadavre/coupled_alarms.git ./coupled_alarms
   ```
2. Configure:
   ```
   coupled_alarms:
     my_alarms:
       entities:
         - alarm_control_panel.alarm_one
         - alarm_control_panel.alarm_two
     other_alarms:
       entities:
         - alarm_control_panel.alarm_x
         - alarm_control_panel.alarm_y
         - alarm_control_panel.alarm_z
   ```
