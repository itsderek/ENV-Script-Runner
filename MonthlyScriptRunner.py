import sys
from os import listdir
from os.path import isfile, join, exists, basename
import datetime
import pyodbc
import re
import csv
import pandas


def main():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    year = last_month.strftime("%Y")
    month = last_month.strftime("%m")

    script_path = "Q:\\Accounting\\Revenue\\{0}\\Revenue Analytics {0}\\SQL Scripts\\".format(year)
    actuals_path = script_path + 'Actuals\\{0}-{1}'.format(year, month)
    ci_path = script_path + 'Consolidated Insurance\\{0}-{1}'.format(year, month)
    revrec_path = script_path + 'Reserve Valuation\\{0}-{1}'.format(year, month)
    estimates_path = script_path + 'Estimates\\{0}-{1}'.format(year, month)
    ge_patient_credits_path = script_path + 'GE Patient Level Refund Liability\\{0}-{1}'.format(year, month)
    aging_by_payor = script_path + 'Aging by Payor\\{0}-{1}'.format(year, month)

    billing_system = billingSystemSelector()

    bs_files = []

    if(billing_system == "All PPM"):
        bs_files.extend(scriptFetcher(actuals_path, "POPEast"))
        bs_files.extend(scriptFetcher(ci_path, "POPEast"))
        bs_files.extend(scriptFetcher(revrec_path, "POPEast"))
        bs_files.extend(scriptFetcher(estimates_path, "POPEast"))

        bs_files.extend(scriptFetcher(actuals_path, "POPSouth"))
        bs_files.extend(scriptFetcher(ci_path, "POPSouth"))
        bs_files.extend(scriptFetcher(revrec_path, "POPSouth"))
        bs_files.extend(scriptFetcher(estimates_path, "POPSouth"))

        bs_files.extend(scriptFetcher(actuals_path, "POPTejas"))
        bs_files.extend(scriptFetcher(ci_path, "POPTejas"))
        bs_files.extend(scriptFetcher(revrec_path, "POPTejas"))
        bs_files.extend(scriptFetcher(estimates_path, "POPTejas"))

        bs_files.extend(scriptFetcher(actuals_path, "PPMMAC"))
        bs_files.extend(scriptFetcher(ci_path, "PPMMAC"))
        bs_files.extend(scriptFetcher(revrec_path, "PPMMAC"))
        bs_files.extend(scriptFetcher(estimates_path, "PPMMAC"))
        bs_files.extend(scriptFetcher(ge_patient_credits_path, "PPMMAC"))
        bs_files.extend(scriptFetcher(aging_by_payor, "PPMMAC"))

        bs_files.extend(scriptFetcher(actuals_path, "Valley"))
        bs_files.extend(scriptFetcher(ci_path, "Valley"))
        bs_files.extend(scriptFetcher(revrec_path, "Valley"))
        bs_files.extend(scriptFetcher(estimates_path, "Valley"))
    else:
        bs_files.extend(scriptFetcher(actuals_path, billing_system))
        bs_files.extend(scriptFetcher(ci_path, billing_system))
        bs_files.extend(scriptFetcher(revrec_path, billing_system))
        bs_files.extend(scriptFetcher(estimates_path, billing_system))
        bs_files.extend(scriptFetcher(ge_patient_credits_path, billing_system))
        bs_files.extend(scriptFetcher(aging_by_payor, billing_system))

    import pprint
    pp = pprint.PrettyPrinter(indent=4, width=200)
    pp.pprint(bs_files)

    assert(len(bs_files) > 0), "There are no scripts for the billing system selected..."
    output = scriptRunner(bs_files)
    displayTotalBalance(output)



def displayTotalBalance(outputDict):
    actuals = 0
    ci = 0
    rev_rec = 0

    for item in outputDict:
        if("AGING CY" in item and "F853" not in item):
            actuals += outputDict[item]['Total Balance'].sum()

        if("Consolidated_Insurance" in item):
            ci += outputDict[item]['Total Balance'].sum()

        if("Flattened_Debits" in item and "New Logic" not in item and "19000101" not in item):
            rev_rec += outputDict[item]['Total Balance'].sum()
        
        if("Credits" in item and "Credits_w0Chgs" not in item and "Detail" not in item and "Patient" not in item and "New Logic" not in item):
            rev_rec += outputDict[item]['Balance_Amount'].sum()

    print("---Actuals---")
    print("${:,.2f}".format(actuals))

    print("---Consolidated Insurance---")
    print("${:,.2f}".format(ci))

    print("---Reserve Valuation---")
    print("${:,.2f}".format(rev_rec))


def scriptFetcher(path, billing_system):
    assert(exists(path)), "The script directory does not exist, have the scripts been created yet?\npath: {}".format(path)

    files = [f for f in listdir(path) if isfile(join(path,f))]

    file_list = []

    if(billing_system == "PPMMAC"):
        for f in files:
            match = re.search(r'\b' + "PPM*", f.upper())
            if(match):
                file_list.append(path + '\\' + f)
    elif(billing_system == "Sheridan_ECW"):
        for f in files:
            match = re.search(r'\b' + billing_system.upper() + r'\b', f.upper())
            if(match):
                file_list.append(path + '\\' + f)

        for f in files:
            match = re.search(r'\b' + "ECW*", f.upper())
            if(match):
                file_list.append(path + '\\' + f)
    else:
        for f in files:
            match = re.search(r'\b' + billing_system.upper() + r'\b', f.upper())
            if(match):
                file_list.append(path + '\\' + f)

    return file_list




def billingSystemSelector():
    print("Which billing system would you like to run?")

    billingSystems = {"1" : "Acute",
                      "2" : "Advocate",
                      "3" : "AS400",
                      "4" : "GE",
                      "5" : "Jupiter_ECW",
                      "6" : "McKesson",
                      "7" : "MediCorp",
                      "8" : "NFPHI",
                      "9" : "Northside",
                      "10" : "POP",
                      "11" : "All PPM",
                      "12" : "POPEast",
                      "13" : "POPSouth",
                      "14" : "POPTejas",
                      "15" : "PPMMAC",
                      "16" : "PracticeMax",
                      "17" : "Pulse",
                      "18" : "Reventics",
                      "19" : "Sheridan_ECW",
                      "20" : "Smart",
                      "21" : "Valley",
                      "22" : "Zotec"}

    print("1. " + billingSystems["1"] + "\t 12. " + billingSystems["12"])
    print("2. " + billingSystems["2"] + "\t 13. " + billingSystems["13"])
    print("3. " + billingSystems["3"] + "\t 14. " + billingSystems["14"])
    print("4. " + billingSystems["4"] + "\t\t 15. " + billingSystems["15"])
    print("5. " + billingSystems["5"] + "\t 16. " + billingSystems["16"])
    print("6. " + billingSystems["6"] + "\t 17. " + billingSystems["17"])
    print("7. " + billingSystems["7"] + "\t 18. " + billingSystems["18"])
    print("8. " + billingSystems["8"] + "\t 19. " + billingSystems["19"])
    print("9. " + billingSystems["9"] + "\t 20. " + billingSystems["20"])
    print("10. " + billingSystems["10"]+ "\t\t 21. " + billingSystems["21"])
    print("11. " + billingSystems["11"] + "\t 22. " + billingSystems["22"])

    user_selection = input("Selection: ")

    if(int(user_selection) < 1 or int(user_selection) > 22):
        print("Please select a valid billing system.")
        sys.exit()

    return billingSystems[user_selection]


def scriptRunner(files):
    driver = 'DRIVER={ODBC Driver 17 for SQL Server};'
    server = 'SERVER'
    database = 'DATABASE'
    credentials = 'Trusted_Connection=yes;'

    connectionString = driver + server + database + credentials

    print("Connecting to the database...")
    connection = pyodbc.connect(connectionString)

    output = {}

    for f in files:
        print("Preparing to run {}...".format(basename(f)))

        with open(f) as s:
            script = re.sub(r'USE DATABASE;', '', s.read(), flags=re.IGNORECASE)

        output[basename(f)] = pandas.read_sql(script, connection)
        output[basename(f)] = output[basename(f)].fillna("NULL")
        output[basename(f)].to_csv(join('Outputs/', basename(f).replace('.sql', '.txt')), index=False, sep='\t')

    connection.close()

    return output


if __name__ == "__main__":
    main()
