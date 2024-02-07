class NoMenuItemFoundError(Exception):
    _message = "No menu item could be found with the name {item_str}"

    def __init__(self, item_name: str) -> None:
        super().__init__(self._message.format(item_str=item_name))
