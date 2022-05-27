# IoT_FridgeChecker
Plotly Dash Webapp visualizes Fridge openings recorded by raspberry pie with magnetic contact switch.

Procedural programming in Python to gather data on fridge usage.
Used cheap "Magnetkontakt"-Schalter bought from Amazon.
Magnet-Switch was wired to raspberry pie.

Two script-files are run on a raspberry pi. 
Using crontab to run those at startup, headless: 
@reboot /home/ubuntu/fridgechecker/WebApp_BUTTON.py
@reboot /home/ubuntu/fridgechecker/logBUTTON_filter.py

What does the "logBUTTON_filter.py" do?

Used Pi GPIO library to detect magnet switch openings. 

Filter -> Set delay value to detect openings with a certain delay

Data Stored in squlite3-Database.


What does the "WebApp_BUTTON.py" do?
Gets data from Database.
Data processed, calculations made with PANDAS.

Creates Dash-Webapp for visualisation: Table averaging fridge-opening-parameters, histogram showing histogram of opening events on in 24 h bins. 
run server on localhost/non-Production

Sources of certain code-sections are denoted in the code-comments. 
