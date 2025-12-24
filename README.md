# Terminal Web App

A centralized data platform for RMS that streamlines employee time tracking, vehicle management, and payroll processing.

## Overview

The RMS Terminal Application is a comprehensive, centralized data platform that aggregates multiple data sources including Geotab, Asana, E-logs, and working hours. It processes this data to provide actionable metrics and critical business information for efficient fleet and workforce management.

## Key Features

### Time & Payroll Management
- **Employee Time Tracking**: Easily track, control, and manage employee hours and kilometers for each work week
- **Review & Request System**: Simple, clear process for handling internal payment issues and approval workflows
- **Payment Dashboard**: Real-time view of expected pay based on time and kilometers worked
- **Payroll Calculations**: Automatic calculation of estimated weekly payroll expenses
- **Monthly Reporting**: Comprehensive monthly reports of hours and payments per individual and company-wide for tax purposes

### Vehicle & Fleet Management
- **Document Database**: Centralized access point for all tracked vehicle documents with automatic notifications
- **Google Calendar Integration**: Vehicle maintenance reminders and scheduling
- **Geotab Integration**: Quick access to vehicle tracking and telematics data

### Employee Management
- **Contact Database**: Centralized employee contact information
- **Automatic Weather Alerts**: Text notifications to drivers about weather conditions
- **Shift Reminders**: Text reminders before shifts to ensure timely clock-ins
- **No-Show Alerts**: Automatic flagging and alerting system for missed shifts

### Productivity & Integration
- **Quick Access Links**: Direct links to Geotab, E-solutions, and Asana
- **Auto Clock-out**: Preventative measures for extended clock-in hours
- **Meal Break Management**: Automatic meal time clock-out functionality

### Security
- **IP Restriction**: Application is locked to specific RMS location IP addresses for enhanced security

## Installation

To install and run the Terminal web app locally, follow these steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/6lack-L/Terminal.git
   ```

2. **Navigate to the project directory**
   ```bash
   cd Terminal
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment variables**
   - Copy `.env.example` to `.env` (if available)
   - Update configuration settings as needed

7. **Start the application**
   ```bash
   python main.py
   ```

## Usage

Once the application is running, open a web browser and navigate to `http://localhost:3000` to access the Terminal interface. 

### Getting Started
1. Log in with your RMS credentials
2. Access the dashboard to view current metrics
3. Use the navigation menu to access different modules (time tracking, vehicle management, payroll, etc.)

**Note**: The application is IP-restricted. Ensure you're accessing it from an authorized RMS location.

## Technology Stack

- **Backend**: Python
- **Frontend**: Web-based interface
- **Integrations**: Geotab API, Asana API, Google Calendar API
- **Database**: (Specify your database system)

## Configuration

Additional configuration may be required for:
- Geotab API credentials
- Asana API access tokens
- Google Calendar API setup
- Email/SMS notification services
- IP whitelist configuration

Refer to the configuration documentation or `.env.example` file for detailed setup instructions.

## Contributing

Contributions are welcome! If you'd like to contribute to the Terminal web app, please follow these guidelines:

1. **Fork the repository**
2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes and commit them**
   ```bash
   git commit -m "Add: description of your changes"
   ```
4. **Push your changes to the branch**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Submit a pull request**

Please ensure your code follows the existing style conventions and includes appropriate tests where applicable.

## License

This project is licensed under the [Apache License](LICENSE).

## Support

For questions, issues, or feature requests, please open an issue on GitHub or contact the RMS development team.

---

**Developed for RMS Fleet & Workforce Management**