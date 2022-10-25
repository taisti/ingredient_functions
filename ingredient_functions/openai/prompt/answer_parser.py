import re
from typing import List
from warnings import warn


class ListParser(object):
    def __init__(self, skip_first: bool = True, lowercase: bool = True) -> None:
        self._skip_first = skip_first
        self._lowercase = lowercase
        self._number_regex = re.compile(rf"([0-9]+)[^a-zA-Z0-9]*")

    def parse(self, response: str) -> List[str]:
        parsed_list = []

        # Filter empty lines
        response_lines = [line for line in response.strip().split("\n") if line]

        for i, line in enumerate(response_lines, start=1):
            if self._skip_first and i == 1:
                line_item = line.strip()

            else:
                match = self._number_regex.match(line)

                if match is None:
                    line_item = line.strip()
                    warn(f"Found no list number in {response} in line {i}:\n\n{line}")

                else:
                    line_item = line[match.end() :].strip()

                    if match.start() != 0:
                        warn(
                            f"List number does not start at 0 in {response} in line {i}:\n\n{line}"
                        )
                    try:
                        list_num = int(match.group(1))
                        if list_num != i:
                            warn(
                                f"List number is incorrect in {response} in line {i}:\n\n{line}"
                            )
                    except ValueError:
                        warn(
                            f"List number is not parsable in {response} in line {i}:\n\n{line}"
                        )

            if line_item:
                if self._lowercase:
                    line_item = line_item.lower()

                parsed_list.append(line_item)

            else:
                warn(f"List item seems empty in {response} in line {i}:\n\n{line}")

        return parsed_list

    def __call__(self, response: str) -> List[str]:
        return self.parse(response=response)
