# Portfolio Tracker CLI

A Python command-line application for managing personal finances, cash accounts, stock investments, and financial goals. The application stores data in a MySQL database and integrates with external APIs for stock market data and USD/EUR exchange rates.

## Features

* Manage cash accounts in multiple currencies
* Buy and sell stocks
* Track stock portfolio value
* Record deposits, withdrawals, and transfers
* Set and monitor financial goals for accounts and the overall portfolio
* View portfolio statistics and progress towards goals
* Automatic USD/EUR currency conversion using live exchange rates
* Store all data in a MySQL database

## Tech Stack

* Python
* MySQL
* MySQL Connector/Python
* Requests
* Alpha Vantage API
* Object-Oriented Programming (OOP)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/raidopaas/portfolio-tracker-cli.git
```

2. Navigate to the project directory:

```bash
cd <portfolio-tracker-cli>
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Create a MySQL database and import the required schema.

5. Configure your API keys.

6. Run the application:

```bash
python main.py
```

## Usage

After launching the application, users can:

* Create and manage cash accounts in EUR and USD.
* Record deposits, withdrawals, and transfers.
* Build and monitor a stock portfolio.
* Track the value of assets across multiple currencies.
* Set financial goals for individual accounts and the overall portfolio.
* Monitor progress towards financial goals.
* View portfolio summaries and account balances.

## Project Structure

```text
Portfolio-Tracker-CLI/
│
├── api/              # External API integrations
├── config/           # Application configuration
├── db/               # Database repositories
├── models/           # Data models
├── services/         # Business logic
├── ui/               # Command-line user interface
├── utils/            # Helper functions
├── main.py           # Application entry point
├── requirements.txt
└── README.md
```

## Future Improvements

Possible features planned for future versions include:

- Display portfolio allocation across accounts (percentages).
- Support additional currencies beyond EUR and USD.
- Dividend change alerts.
- Track liabilities such as loans and mortgages.
- Portfolio performance history and visual charts.
- CSV import/export for transactions.