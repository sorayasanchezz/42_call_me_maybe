from pydantic import BaseModel, field_validator


class TypeInfo(BaseModel):
    """The type of a parameter or of a return value.

    Attributes:
        type: The name of the type, like "number" or "string".
    """

    type: str


class FunctionDefinition(BaseModel):
    """One function from the menu (functions_definition.json).

    Attributes:
        name: The name of the function, like "fn_add_numbers".
        description: What the function does.
        parameters: The name and the type of every parameter.
        returns: The type of the value the function gives back.
    """

    name: str
    description: str
    parameters: dict[str, TypeInfo]
    returns: TypeInfo

    @field_validator("parameters")
    @classmethod
    def check_parameter_types(
        cls, parameters: dict[str, TypeInfo]
    ) -> dict[str, TypeInfo]:
        """Refuse a parameter with a type we cannot write.

        Only the parameters are checked: the program never writes
        the return value, so "returns" can have any type.
        Example: a parameter of type "array" is refused.

        Args:
            parameters: The name and the type of every parameter.

        Returns:
            The same parameters, if all their types are known.

        Raises:
            ValueError: If a type is not in known_types.
        """
        known_types = ["number", "integer", "string", "boolean"]
        for name, type_info in parameters.items():
            if type_info.type not in known_types:
                raise ValueError(
                    f"parameter '{name}' has an unknown type: "
                    f"{type_info.type}"
                )
        return parameters


class PromptItem(BaseModel):
    """One question from function_calling_tests.json.

    Attributes:
        prompt: The question written by the user.
    """

    prompt: str
