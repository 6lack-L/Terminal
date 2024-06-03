# Terminal Web App

This directory contains the source code for the Terminal web app.

## Overview

The Terminal web app is a command-line interface (CLI) tool that allows users to interact with a remote server through a web browser. It provides a familiar command-line environment with features such as command execution, file management, and remote server access.

## Features

Main functions:
  •	A system to easily track control and mange employee hours/kms for work week. review request features to allow a simple clear process for internal payment issues
  •	payment dashboard (possible view options to view in real time expected pay for time/km worked.) calculate estimated weekly payroll expense.
  •	monthly report of hours and payment per individuals and companywide for taxes.
  •	IP locked to specific RMS Locations.
Features:
  •	database access point for all tracked vehicle documents, automatic notifications.
  •	google calendar for vehicle reminders.
  •	employee contact database.
  •	quick access to Geotab, E-solutions, and Asana.
  •	Automatic weather text notifications to drivers.
  •	Preventative measures for extended clock in hours, Auto Clock-out
  •	Mealtime clock-out
  •	*Text reminders before shifts to clock in after set time flag employee as no show and send alert back for new driver

## Installation

To install and run the Terminal web app locally, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/terminal-web-app.git`
2. Navigate to the project directory: `cd terminal-web-app`
4. create vitual environment: `python -m venv /path/to/new/virtual/environment`
6. start virtual environment : `source venv/bin/activate`
7. Install dependencies: `pip install -r requirements`
8. Start the web app: `python main.py`

## Usage

Once the web app is running, open a web browser and navigate to `http://localhost:3000` to access the Terminal interface. From there, you can start interacting with the remote server using the provided command-line interface.

## Contributing

Contributions are welcome! If you'd like to contribute to the Terminal web app, please follow these guidelines:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m "Add your commit message"`
4. Push your changes to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request.

## License

This project is licensed under the [Apache License](LICENSE).
