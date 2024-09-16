from CustomResponse import CustomResponse
from tabulate import tabulate
import re


def dataflows(response: CustomResponse) -> list:
    """
    Extracts relevant information from the inquired dataflows.
    Each dataflow has it's properties stored in a dictionary.
    Adds the dictionaries to a list.
    """
    dataflows = []
    for dataflow in response.hierarchy.findall(
        f".//{response.find_namespace('structure')}Dataflow"
    ):
        agency_id = dataflow.attrib["agencyID"]
        dataflow_id = dataflow.attrib["id"]
        dataflow_name = ""
        dataflow_names = dataflow.findall(f"./{response.find_namespace('common')}Name")
        for name in dataflow_names:
            if name.attrib[r"{http://www.w3.org/XML/1998/namespace}lang"] == "en":
                dataflow_name = name.text.replace("\r", "").replace("\n", "")
                dataflow_name = re.sub(" +", " ", dataflow_name)
                break
            else:
                continue
        dataflow_structure = dataflow.find(
            f"./{response.find_namespace('structure')}Structure"
        )
        if dataflow_structure is not None:
            dataflow_reference = dataflow_structure.find("./Ref")
            reference_id = dataflow_reference.attrib["id"]
            reference_agencyID = dataflow_reference.attrib["agencyID"]
            reference_class = dataflow_reference.attrib["class"]
        else:
            reference_id = "None"
            reference_agencyID = "None"
            reference_class = "None"
        dataflows.append(
            {
                "dataflow_id": dataflow_id,
                "agency_id": agency_id,
                "dataflow_name": dataflow_name,
                "reference_id": reference_id,
                "reference_agencyID": reference_agencyID,
                "reference_class": reference_class,
            }
        )
    return dataflows


def codelists(response: CustomResponse) -> list:
    """
    Extracts relevant information from the inquired codelists.
    Each code has it's properties stored in a dictionary.
    Adds the dictionaries to a list.
    """
    codelists = []
    for codelist in response.hierarchy.findall(
        f".//{response.find_namespace('structure')}Codelist"
    ):
        agency_id = codelist.attrib["agencyID"]
        codelist_id = codelist.attrib["id"]
        codelist_names = codelist.findall(f"./{response.find_namespace('common')}Name")
        codelist_name = ""
        for name in codelist_names:
            if name.attrib[r"{http://www.w3.org/XML/1998/namespace}lang"] == "en":
                codelist_name = name.text.replace("\r", "").replace("\n", "")
                codelist_name = re.sub(" +", " ", codelist_name)
                break
            else:
                continue
        codes = codelist.findall(f"./{response.find_namespace('structure')}Code")
        for code in codes:
            code_id = code.attrib["id"]
            code_name = ""
            code_names = code.findall(f"./{response.find_namespace('common')}Name")
            for name in code_names:
                if name.attrib[r"{http://www.w3.org/XML/1998/namespace}lang"] == "en":
                    code_name = name.text.replace("\r", "").replace("\n", "")
                    code_name = codelist_name = re.sub(" +", " ", code_name)
                    break
                else:
                    continue
            parent = code.find(f"./{response.find_namespace('structure')}Parent")
            if parent is not None:
                code_reference = parent.find("./Ref")
                code_parent = code_reference.attrib["id"]
            else:
                code_parent = "None"
            codelists.append(
                {
                    "agency_id": agency_id,
                    "codelist_id": codelist_id,
                    "codelist_name": codelist_name,
                    "code_id": code_id,
                    "code_name": code_name,
                    "code_parent": code_parent,
                }
            )
    return codelists


def output_dataflows(out: list) -> None:
    """
    Writes the list of dataflows to an output file.
    """
    with open("dataflows.txt", "w") as file:
        file.write(tabulate(out, "keys"))


def output_codelists(out: list) -> None:
    """
    Writes the list of codelists to an output file.
    """
    with open("codelists.txt", "w") as file:
        file.write(tabulate(out, "keys"))
