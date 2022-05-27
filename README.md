# IoT_FridgeChecker
Plotly Dash Webapp visualizes Fridge openings recorded by raspberry pie with magnetic contact switch.

Procedural programming in Python to gather data on fridge usage.
Used cheap "Magnetkontakt"-Schalter bought from Amazon.
Magnet-Switch was wired to raspberry pie.

Two script-files are run on a raspberry pi. 
Using crontab to run those at startup, headless: 
@reboot /home/ubuntu/fridgechecker/bin/python /home/ubuntu//IoT_FridgeChecker/App.py > /home/ubuntu/fridgechecker/logApp.txt 2>&1
@reboot /home/ubuntu/fridgechecker/bin/python /home/ubuntu//IoT_FridgeChecker/Logger.py > /home/ubuntu/fridgechecker/logLogger.txt 2>&1


What does the "Logger.py" do?

Used Pi GPIO library to detect magnet switch openings. 
Filter -> Set delay value to detect openings with a certain delay
Data Stored in squlite3-Database.


What does the "App.py" do?
Gets data from Database.
Data processed, calculations made with PANDAS.

Creates Dash-Webapp for visualisation: Table averaging fridge-opening-parameters, histogram showing histogram of opening events on in 24 h bins. 
run server on localhost/non-Production

