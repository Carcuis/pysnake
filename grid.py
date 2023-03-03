import numpy as np
import numpy.typing as npt


class Grid:
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.contents: npt.NDArray[np.uint8] = np.zeros((height, width), dtype=np.uint8)
        self.type_dict: dict[str, int] = {
            'nothing': 0, 'wall': 1, 'body': 100,
            # food: [10, 100)
            'apple': 10, 'beef': 11, 'iron': 12, 'gold': 13, 'slimeball': 14, 'heart': 15
        }
        self.type_dict_inv: dict[int, str] = {v: k for k, v in self.type_dict.items()}

    def __getitem__(self, key):
        return self.contents.__getitem__(key)

    def __setitem__(self, key, value):
        self.contents.__setitem__(key, value)

    def check_type(self, _type: str, dict_only=True) -> None:
        """ check if `_type` in Grid.type_dict, set dict_only=False to allow `body on` sth. """
        if not dict_only:
            if _type.startswith("body on "):
                # cut it off
                _type = _type[len("body on "):]
        if _type not in self.type_dict.keys():
            raise ValueError(f"Invalid type: '{_type}', not in {list(self.type_dict.keys())}")

    def check_type_value(self, value: int) -> None:
        """ check if `value` or `value - 100` in Grid.type_dict """
        if value <= 100:
            _value = value
            _str = f"{value}"
        else:
            _value = value - 100
            _str = f"{value} or {_value}"
        if _value not in self.type_dict.values():
            raise ValueError(f"Invalid value: {_str}, not in {list(self.type_dict.values())}")

    def get_size(self) -> tuple[int, int]:
        return self.width, self.height

    def get_value(self, x: int, y: int) -> int:
        """ get the original value of a cell, x: column, y: row """
        return self.contents[y, x]

    def set_value(self, x: int, y: int, value: int) -> None:
        """ set the original value of a cell, x: column, y: row """
        self.check_type_value(value)
        self.contents[y, x] = value

    def get_type(self, x: int, y: int, ignore_body=False) -> str:
        """ get the `type` of a cell, return full type (e.g. `body on wall`) unless set ignore_body=True """
        value = self.get_value(x, y)
        if value < 100:
            return self.type_dict_inv[value]
        value_under_body = value % 100
        body = "body on " if not ignore_body else ""
        return f"{body}{self.type_dict_inv[value_under_body]}"

    def set_type(self, x: int, y: int, new_type: str, replace=False) -> None:
        """
        set the `type` of cell in Grid.type_dict,
        if type == body then `body` will be set *on* `old type`,
        set replace=True to replace the content of a cell,
        type: `body on sth.` is allowed in this case or when the cell is empty
        """
        self.check_type(new_type, dict_only=False)
        if replace or self.is_empty(x, y):
            if new_type.startswith("body on "):
                # cut it off
                new_type = new_type[len("body on "):]
                new_type_value = self.type_dict[new_type] + 100
            else:
                new_type_value = self.type_dict[new_type]
        else:
            # cell not empty, allow only body on something, default
            old_type = self.get_type(x, y)
            old_type_value = self.get_value(x, y)
            if new_type != 'body':
                raise ValueError(f"Cannot set type '{new_type}' to cell: cell not empty. Current: '{old_type}'.")
            if self.has_body(x, y):
                new_type_value = old_type_value
            else:
                new_type_value = old_type_value + 100
        self.set_value(x, y, new_type_value)

    def set_body(self, x: int, y: int) -> None:
        self.set_type(x, y, 'body')

    def clear_type(self, x: int, y: int, _type: str) -> None:
        """ clear a specific `_type` of a cell if it has """
        self.check_type(_type, dict_only=True)
        if self.has_type(x, y, _type):
            self.set_value(x, y, self.get_value(x, y) - self.type_dict[_type])

    def is_type(self, x: int, y: int, _type: str) -> bool:
        """ check if the full type of cell == `_type` """
        self.check_type(_type, dict_only=False)
        return self.get_type(x, y) == _type

    def is_empty(self, x: int, y: int) -> bool:
        return self.get_value(x, y) == 0

    def has_food(self, x: int, y: int) -> bool:
        value = self.get_value(x, y)
        if 10 <= value < 100 or 110 <= value < 200:
            return True
        return False

    def has_wall(self, x: int, y: int) -> bool:
        return self.get_value(x, y) in (1, 101)

    def has_body(self, x: int, y: int) -> bool:
        return self.get_value(x, y) >= 100

    def has_type(self, x: int, y: int, _type: str) -> bool:
        """ check if cell has a specific `_type` """
        self.check_type(_type, dict_only=True)
        if self.has_body(x, y):
            if _type == 'body':
                return True
            current_type = self.get_type(x, y)[len("body on "):]
        else:
            current_type = self.get_type(x, y)
        return current_type == _type

    def get_empty_count(self) -> int:
        """ get the count of empty cells """
        return self.height * self.width - np.count_nonzero(self.contents)

    def clear_cell(self, x: int, y: int) -> None:
        """ clear one cell """
        self.set_value(x, y, 0)

    def clear_all(self) -> None:
        """ clear the entire map """
        self.contents.fill(0)

    def display(self) -> None:
        print(self.contents)


if __name__ == '__main__':
    # test
    grid = Grid(5, 5)
    print(grid.contents)
    print("empty count: ", grid.get_empty_count(), "\n")
    grid[1, 2] = 101
    print("set: grid[1, 2] = 101\n", grid.contents)
    print("empty count: ", grid.get_empty_count(), "\n")
    print("value of (1, 2): ", grid[1, 2])
    print("type of (1, 2): ", grid.get_type(1, 2))
    print("type of (1, 2), ignored body: ", grid.get_type(1, 2, ignore_body=True))
    print(f"{grid.is_type(1, 2, 'body') = }")
    print(f"{grid.has_body(1, 2) = }")
    print("-" * 20)
    grid.set_type(0, 1, 'wall')
    print(f"set_type(0, 1, 'wall')\n{grid.get_type(0, 1) = }\n")
    grid.set_type(0, 1, 'body')
    print(f"set_type(0, 1, 'body')\n{grid.get_type(0, 1) = }\n")
    grid.set_type(0, 1, 'iron', replace=True)
    print(f"set_type(0, 1, 'iron', replace=True)\n{grid.get_type(0, 1) = }\n")
    grid.set_type(0, 1, 'body on apple', replace=True)
    print(f"set_type(0, 1, 'body on apple', replace=True)\n{grid.get_type(0, 1) = }")
    print(f"{grid.has_type(0, 1, 'body') = }\n")
    grid.clear_type(0, 1, 'body')
    print(f"clear_type(0, 1, 'body')\n{grid.get_type(0, 1) = }\n")
