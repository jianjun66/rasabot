## Generated Story 8265409989699089755
* ask_program
    - utter_ask_interest
    - action_search_programs
* inform{"interest": "animal"}
    - slot{"interest": "animal"}
    - utter_ask_amount
    - action_search_programs
* inform{"interest": "human"}
    - slot{"interest": "human"}
    - utter_ask_amount
    - action_search_programs
* inform{"interest": "environment"}
    - slot{"interest": "environment"}
    - utter_ask_amount
    - action_search_programs

## Happy
* greet
    - utter_greet
    - utter_ask_whichprogram
* inform{"program": "donation"}
    - slot{"program": "donation"}
    - utter_ask_interest
    - action_search_programs
* inform{"program": "volunteer"}
    - slot{"program": "volunteer"}
    - utter_ask_location
    - action_search_programs
