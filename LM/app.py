import flask
from webui import WebUI
import numpy as np
import numpy_financial as npf
import pandas as pd

app = flask.Flask(__name__, template_folder='templates')
ui = WebUI(app, debug=True)

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':

        # Set the value of the home you are looking to buy
        home_value = int(flask.request.form['home_value'])

        # What percentage are you paying up-front?
        down_payment_percent = int(flask.request.form['down_payment_percent'])/100

        # Set the mortgage rate
        mortgage_rate = int(flask.request.form['mortgage_rate'])/100

        # Set number of years of loan
        years = int(flask.request.form['years'])

        # Set payment schedule (monthly)
        schedule = 12

        ################################################################

        # Calculate the dollar value of the down payment
        down_payment = home_value * down_payment_percent
        print("Initial Down Payment: " + str(down_payment))

        # Calculate the value of the mortgage loan required after the down payment
        mortgage_loan = home_value - down_payment
        print("Mortgage Loan: " + str(mortgage_loan))

        # Derive the equivalent monthly mortgage rate from the annual rate
        mortgage_rate_periodic = ((1+mortgage_rate)**(1/schedule) - 1)

        # How many monthly payment periods will there be over 30 years?
        mortgage_payment_periods = schedule*years

        # Calculate the monthly mortgage payment (multiply by -1 to keep it positive)
        periodic_mortgage_payment = -1*npf.pmt(rate=mortgage_rate_periodic, nper=mortgage_payment_periods, pv=mortgage_loan)
        print("Monthly Mortgage Payment: " + str(round(periodic_mortgage_payment, 2)))

        ##############################################################

        # Calculate the amount of the first loan payment that will go towards interest
        initial_interest_payment = mortgage_loan * mortgage_rate_periodic
        print("Initial Interest Payment: " + str(round(initial_interest_payment, 2)))

        # Calculate the amount of the first loan payment that will go towards principal
        initial_principal_payment = periodic_mortgage_payment - initial_interest_payment
        print("Initial Principal Payment: " + str(round(initial_principal_payment, 2)))

        ##############################################################

        # Initialize principal_remaining variable is  as an array of 0's with length equal to the number of payment periods
        interest_paid = np.zeros(mortgage_payment_periods)
        principal_paid = np.zeros(mortgage_payment_periods)
        principal_remaining = np.zeros(mortgage_payment_periods)

        # Loop through each mortgage payment period
        for i in range(0, mortgage_payment_periods):
            
            # Handle the case for the first iteration
            if i == 0:
                previous_principal_remaining = mortgage_loan
            else:
                previous_principal_remaining = principal_remaining[i-1]
                
            # Calculate the interest and principal payments
            interest_payment = round(previous_principal_remaining*mortgage_rate_periodic, 2)
            principal_payment = round(periodic_mortgage_payment-interest_payment, 2)
            
            # Catch the case where all principal is paid off in the final period
            if previous_principal_remaining - principal_payment < 0:
                principal_payment = round(previous_principal_remaining,2)
            
            # Collect the historical values
            interest_paid[i] = interest_payment
            principal_paid[i] = principal_payment
            principal_remaining[i] = previous_principal_remaining - principal_payment

        #######################################################################################        

        # Calculate the cumulative home equity (principal) over time
        cumulative_home_equity = np.cumsum(principal_paid)

        # Calculate the cumulative interest paid over time
        cumulative_interest_paid = np.cumsum(interest_paid)

        # Calculate your percentage home equity over time
        cumulative_percent_owned = down_payment_percent + (cumulative_home_equity/home_value)

        return flask.render_template('loan.html', downpayment = down_payment, mortgageloan = mortgage_loan, periodicmortgagepayment = round(periodic_mortgage_payment), initialinterestpayment = round(initial_interest_payment), initialprincipalpayment = round(initial_principal_payment))

if __name__ == '__main__':
    ui.run()
