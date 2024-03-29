### API to calculate premiums for Prometheon

#### 1. Description
API designed for Azure deployment. The data for the calculation of  the premium
is obtained from the prometheon Azure SQL Database. The /quote endpoint expects a
JSON with the following keys:

- amount
- timestamp (string: '%Y-%m-%d')
- ground_handlers (list)
- airports (list)

Upon successful retrieval of the premium, the API returns the premium price (float),
and the quote_reply (JSON), where the calculation parameters are detailed

#### 2. Implementation
In main.py, the Flask app is defined, with a single endpoint: /quote.


In resources/quote, the parsing of inputs is dealt with, the actual quote function
is called (from models/premium), and the values are returned.

In models/premium the premium_calculation function is defined.
In models/user a user interface is defined, which is most likely not needed

To interact with the Azure SQL database, the pyodbc package is used. This package
cannot be easily installed for Python 3.4. Azure only supports 2.7 or 3.4 by default.
By adding the Py3.6 extension on Azure, modifying web.config, getting rid of runtime.txt, and adding
.skipPythonDeployment (which tries to pip install -r requirements.txt with Python 3.4),
and doing the pip install on Azure using the KUDU command line interface, the app runs
successfully on Python 3.6.

Note that by addition of

<system.webServer>
  <httpErrors errorMode="Detailed"></httpErrors>
  ....

in web.config, one gets extensive error messages for debugging.

#### 3. Deployment
Using the local git command line. There are two remotes: origin (on github) and azure.
Pushing to azure results in automatic deployment.


#### 4. Issues
Numpy seems to get installed in a faulty fashion by pip on Azure. Unclear how to
solve this. The easy workaround: avoid numpy. It is not really necessary to use it.

The http is not secure (no https://)

There is no authentification (this can be done on Azure)

##### 5. Status and Next steps
- An SQLite implementation for premium calculation is still in models/premium,
but commented out.
- The Azure SQL connection is only there for test purposes. So the next step is
to define the premium calculation for Azure SQL
- The interface with Sharepoint needs to be defined: what is communicated back and
forward exactly?
