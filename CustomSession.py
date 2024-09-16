from requests import Session, RequestException
from CustomResponse import CustomResponse


class CustomSession(Session):
    """
    Class for managing API sessions getting OECD resources (building the api, sending request).
    Inherits from "requests.Session".
    """

    def __init__(self, args=None) -> None:
        super().__init__()

        self.headers = {
            "Accept": "application/vnd.sdmx.structure+xml; charset=utf-8; version=2.1",
            "Accept-Language": "en",
            "Accept-Encoding": "gzip, deflate, br",
        }
        query_types = {"1": "structure", "2": "data"}
        url_root = "https://sdmx.oecd.org/public/rest/v2"
        """
        leading string of the url for identifying any resource, using the OECD endpoint
        """

        if args is None:
            query_type = input(
                "\nWhat would you like to query?\n"
                + "1. Structural Metadata\n"
                + "2. Data & Reference Metadata\n"
                + "\nInput the number corresponding to an option: "
            )

            while True:
                if query_type not in query_types.keys():
                    query_type = input(f"Choose a valid option: {query_types.keys()}: ")
                    continue
                else:
                    self.query_type = query_types[query_type]
                    break
            url_tail = ""
            if self.query_type == "structure":
                self.headers["Accept"] = (
                    "application/vnd.sdmx.structure+xml; charset=utf-8; version=2.1"
                )
                self.artefact_type = input(f"Input the artefact type: ")
                url_tail = f"{self.query_type}/{self.artefact_type}"
            elif self.query_type == "data":
                self.headers["Accept"] = (
                    "application/vnd.sdmx.structurespecificdata+xml; charset=utf-8; version=2.1"
                )
                context = input("\nInput the context: ")
                agency_id = input("Input the agency identifier: ")
                dataflow_id = input("Input the dataflow identifier: ")
                dataflow_version = input("Input the dataflow version: ")
                filter_expression = input(
                    'Input the filter expression \n(combination of dimension values, except "Time Period"): '
                )
                optional_parameters = input(
                    'Input the optional parameters \n(dimension value "Time Period", attributes and measures): '
                )
                url_tail = f"{self.query_type}/{context}/{agency_id}/{dataflow_id}/{dataflow_version}/{filter_expression}?{optional_parameters}"
                """
                trailing string of the url for identifying a specific resource
                """
            self.url = "/".join([url_root, url_tail])
            return

        else:
            query_type = args[0]
            if query_type not in query_types.values():
                raise RequestException(f'"{query_type}" not in {query_types.values()}')
            else:
                self.query_type = query_type
                if self.query_type == "structure":
                    self.headers["Accept"] = (
                        "application/vnd.sdmx.structure+xml; charset=utf-8; version=2.1"
                    )
                    self.artefact_type = args[1]
                    url_tail = f"{self.query_type}/{self.artefact_type}"
                elif self.query_type == "data":
                    self.headers["Accept"] = (
                        "application/vnd.sdmx.structurespecificdata+xml; charset=utf-8; version=2.1"
                    )
                    context = args[1]
                    agency_id = args[2]
                    dataflow_id = args[3]
                    dataflow_version = args[4]
                    filter_expression = args[5]
                    optional_parameters = args[6]
                    url_tail = f"{self.query_type}/{context}/{agency_id}/{dataflow_id}/{dataflow_version}/{filter_expression}?{optional_parameters}"
                    """
                    trailing string of the url for identifying a specific resource
                    """
                self.url = "/".join([url_root, url_tail])
                return

    def get(self) -> CustomResponse:
        """
        Overwritten "get" method, inherited from "requests.Session".
        Instead of a regular "requests.Response", instantiates and returns a "CustomResponse()" object.
        """
        response = super().get(self.url, headers=self.headers)
        if response.status_code != 200:
            raise RequestException(
                f"Something went wrong! Status code: <{response.status_code}>"
            )
        else:
            print(f"All good! Status code: <{response.status_code}>")
            print("Processing the response...")
            custom_response = CustomResponse(response)
            return custom_response
