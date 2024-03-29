from rest_framework.parsers import BaseParser


class OctetStreamParser(BaseParser):
    """
    Octet Stream parser
    """

    media_type = "application/octet-stream"

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()
