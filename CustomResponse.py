import re
from requests import Response
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element


class CustomResponse(Response):
    """
    Class for managing(wrapping, decoding, displaying) responses to OECD API calls.
    Inherits from "requests.Response()".
    """

    def __init__(self, response: Response) -> None:
        super().__init__()
        self.__dict__.update(response.__dict__)
        self.hierarchy = self.get_xml_hierarchy()
        """
        The XML response as an element tree.
        """
        self.namespaces = self.get_namespaces()
        """
        The namespaces prefixing the node tags in the element tree.
        """

    def detail(self) -> None:
        """
        Prints relevant response information.
        """
        indent = " " * 4
        print("\nResponse details: ")
        print(indent + f"- Code: {self.status_code}\t")
        print(indent + "- Headers: ")
        indent *= 2
        for key, val in self.headers.items():
            print(indent + "-> " + key, ":", val)
        return

    def get_namespaces(self) -> list:
        """
        Finds all the namespaces prefixing the node tags.
        """
        namespaces = []
        for element in self.hierarchy.iter():
            if namespace := re.search(r"^({.+})", element.tag):
                namespace = namespace.group(1)
                if namespace not in namespaces:
                    namespaces.append(namespace)
                else:
                    pass
        return namespaces

    def get_namespace_descriptions(self) -> list:
        """
        Each namespace is assigned a description, and added to a list as a dictionary, with:
        - the description as key
        - the namespace as value
        """
        namespace_descriptions = []
        for namespace in self.namespaces:
            namespace_descriptions.append(
                {
                    "description": re.search(r"/v2_1/(.+)}$", namespace).group(1),
                    "namespace": namespace,
                }
            )
        return namespace_descriptions

    def find_description(self, namespace: str) -> str:
        """
        Iterates through the list of descriptions and finds the description corresponding to the namespace.
        """
        description = ""
        for d in self.get_namespace_descriptions():
            if d["namespace"] == namespace:
                description = d["description"]
                break
            else:
                pass
        return description

    def find_namespace(self, description: str) -> str:
        """
        Iterates through the list of descriptions and finds the namespace corresponding to the description.
        """
        for d in self.get_namespace_descriptions():
            if d["description"] == description:
                namespace = d["namespace"]
                break
            else:
                pass
        return namespace

    def print_namespaces(self) -> None:
        """
        Prints the namespaces.
        """
        print("\nXPath namespaces: ")
        for name in self.namespaces:
            print("-> " + name)
        print("\n")

    def get_xml_hierarchy(self) -> Element:
        """
        Parses the XML response and returns it's tree structure.
        """
        root = ET.fromstring(self.content)
        return root

    def printable_hierarchy(self, element=None, level=0) -> list:
        """
        Prepares the tree structured response to be outputted:
        - navigates the tree by recursion
        - takes into account the hierarchy level each node finds itself in
        - extracts and prettyfies the contents: tags, attributes, text
        - prepares a list with the individual nodes of the tree as elements
        - the order of the nodes in the list is hierarchical
        """
        if element is None:
            element = self.hierarchy
        to_display = []
        indent = (" " * 4) * level
        tag = element.tag
        if element.attrib.items():
            attributes = ", ".join(
                f'{re.sub(r"^({.+})", "", k)}="{v}"' for k, v in element.attrib.items()
            )
        else:
            attributes = "None"
        if element.text is not None:
            text = element.text.replace("\n", "").replace("\r", "")
            text = re.sub(" +", " ", text)
        else:
            text = "None"
        node = f"{indent}{tag} [Attributes: {attributes}]: {text}"
        to_display.append(node)
        for child in element:
            to_display.extend(self.printable_hierarchy(child, level + 1))
        return to_display

    def output_hierarchy(self, rng=None) -> None:
        """
        Further prettyfies the response and writes it to an output file.
        """
        namespaces = self.namespaces
        printable = self.printable_hierarchy()
        for i in range(len(printable)):
            for n in namespaces:
                if printable[i].strip().startswith(n):
                    description = self.find_description(n)
                    printable[i] = re.sub(n, f"-> ({description}) ", printable[i])
                    break
                else:
                    pass
        with open("hierarchy.txt", "w") as file:
            file.write("XPath resource hierarchy:" + "\n" + "=" * 50 + "\n")
            if rng == None:
                for i in printable:
                    file.write(i + "\n")
            else:
                for i in printable[:rng]:
                    file.write(i + "\n")
