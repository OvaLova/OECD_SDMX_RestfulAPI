from requests import RequestException
from CustomSession import CustomSession
import standalone_functions as fct
import sqlite3
import sys


def query() -> None:
    """
    Function for running API queries requesting OECD resources.
    Takes a command-line argument specifying the run mode.
    Can be run in two modes:
    * intercatively (without taking other command-line arguments)
    * automatically (taking additional command-line arguments)
    """

    if len(sys.argv) >= 2:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            if len(sys.argv) == 2:
                while True:
                    session = CustomSession()
                    print(f"\nSession's resulting API: {session.url}")
                    try:
                        print("Sending request to endpoint, waiting for response...")
                        response = session.get()
                        break
                    except RequestException as e:
                        print(f'\nCaught an exception: "{e}"')
                        continue

                response.detail()
                print(
                    "\nPrettyfying the response and writing it to the output file(hierarchy.txt)..."
                )
                response.output_hierarchy()
                print("Operation completed!")
                if session.query_type == "structure":
                    if session.artefact_type == "dataflow":
                        print(
                            "\nExtracting relevant information from the inquired dataflows and writing it to the output file(dataflows.txt)..."
                        )
                        fct.output_dataflows(fct.dataflows(response))
                        print("Operation completed!")
                    elif session.artefact_type == "codelist":
                        print(
                            "\nExtracting relevant information from the inquired codelists and writing it to the output file(codelists.txt)..."
                        )
                        fct.output_codelists(fct.codelists(response))
                        print("Operation completed!")
                    else:
                        pass
                else:
                    pass
                print("\nWorkflow completed!")

                while True:
                    match input("Would you like to query some more? ").lower():
                        case "yes" | "y":
                            query()
                        case "no" | "n":
                            sys.exit("End of session, EXITED\n")
                        case _:
                            print('Choose a valid option: "yes"/"y" or "no"/"n"')

            else:
                sys.exit("Interactive mode does not take other arguments\n")
        elif sys.argv[1] == "--shell" or sys.argv[1] == "-s":
            if len(sys.argv) == 2:
                sys.exit(
                    "Shell mode requires additional arguments, at least two more (for the query type and for the artefact/context)\n"
                )
            else:
                if (len(sys.argv) == 4 and sys.argv[2] == "structure") or (
                    len(sys.argv) == 9 and sys.argv[2] == "data"
                ):
                    args = []
                    for arg in sys.argv[2:]:
                        args.append(arg)
                    session = CustomSession(args)
                    print(f"\nSession's resulting API: {session.url}")
                    try:
                        print("Sending request to endpoint, waiting for response...")
                        response = session.get()
                    except RequestException as e:
                        sys.exit(f'\nCaught an exception: "{e}"\n')

                    response.detail()
                    print(
                        "\nPrettyfying the response and writing it to the output file(hierarchy.txt)..."
                    )
                    response.output_hierarchy()
                    print("Operation completed!")
                    if session.query_type == "structure":
                        if session.artefact_type == "dataflow":
                            print(
                                "\nExtracting relevant information from the inquired dataflows and writing it to the output file(dataflows.txt)..."
                            )
                            fct.output_dataflows(fct.dataflows(response))
                            print("Operation completed!")
                        elif session.artefact_type == "codelist":
                            print(
                                "\nExtracting relevant information from the inquired codelists and writing it to the output file(codelists.txt)..."
                            )
                            fct.output_codelists(fct.codelists(response))
                            print("Operation completed!")
                        else:
                            pass
                    else:
                        pass
                    print("\nWorkflow completed!")
                else:
                    if sys.argv[2] == "structure":
                        sys.exit(
                            "For structure queries, only one more argument needed after the query type: \n"
                            "* artefact\n"
                        )
                    elif sys.argv[2] == "data":
                        sys.exit(
                            "For data queries, 6 more arguments needed after the query type: \n"
                            "* context\n"
                            "* agency_id\n"
                            "* dataflow_id\n"
                            "* dataflow_version\n"
                            "* filter_expression\n"
                            "* optional_parameters\n"
                        )
                    else:
                        sys.exit('Supported query types: "structure" and "data"\n')
        else:
            sys.exit('Choose mode among: "--interactive"|"-i" or "--shell"|"-s"\n')
    else:
        sys.exit("Provide at least one argument to specify the run mode\n")


def extract_fromDB(table: str, attribute: str) -> list:
    """
    Function for extracting an attribute(column values) from a table inside the Macro.db sqlite3 database.
    Purpose: extract to compare with the API response.
    The DB extracted attribute values should be a subset of the values(codes) extracted, via API, from the codelist of that attribute
    """
    cx = sqlite3.connect("Macro.db")
    cu = cx.cursor()
    selected = []
    for row in cu.execute(f"SELECT DISTINCT {attribute} FROM {table};"):
        row = row[0]
        if table == "subjects":
            if row.startswith("OECD"):
                row = "OECD"
            elif row.startswith("Euro area"):
                row = "Euro area"
            elif row.startswith("European Union"):
                row = "European Union"
            elif "China" in row:
                row = "China"
            else:
                pass
        else:
            pass
        selected.append(row)
    print(f"\n{selected}\n")
    return selected


def extract_fromAPI(what: str) -> list:
    """
    Function for extracting all possible values(codes) from one of the codelists, via API:
    * "CL_AREA", codelist for the locations (in DB, corresponding to the attribute "name" in the "subjects" table)
    * "CL_TRANSACTION", codelist for the transactions (in DB, corresponding to the attribute "name" in the "indicators" table)
    * "CL_MEI_TEST_UNIT_MEASURE", codelist for the measure units (in DB, corresponding to the attribute "unit" in the "measures" table)
    Purpose: extract to compare with the DB attribute values.
    The API extracted codelist values(codes) should be a superset of the corresponding DB extracted attribute values.
    """
    cl_session = CustomSession(["structure", "codelist"])
    print(f"\nSession's resulting API: {cl_session.url}")
    try:
        print("Sending request to endpoint, waiting for response...")
        cl_response = cl_session.get()
    except RequestException as e:
        print(f'\nCaught an exception: "{e}"')
    cl = fct.codelists(cl_response)
    list_ = []
    match what:
        case "subject":
            for code in cl:
                if code["agency_id"] == "OECD" and code["codelist_id"] == "CL_AREA":
                    subject = code["codelist_name"]
                    list_.append(subject)
        case "indicator":
            for code in cl:
                if (
                    code["agency_id"] == "OECD.SDD.NAD"
                    and code["codelist_id"] == "CL_TRANSACTION"
                ):
                    indicator = code["codelist_name"]
                    list_.append(indicator)
        case "unit":
            for code in cl:
                if (
                    code["agency_id"] == "OECD.SDD.SDPS"
                    and code["codelist_id"] == "CL_MEI_TEST_UNIT_MEASURE"
                ):
                    unit = code["codelist_name"]
                    list_.append(unit)
        case _:
            sys.exit("Not a viable option")
    print(f"{list_}\n")
    return list_


def main() -> None:
    query()


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        sys.exit("\nProgram execution ended: EXITED\n")
