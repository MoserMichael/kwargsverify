import types
import re
import validate_email

def strip_leading_trailing_space():
    def stip_spaces(_, param_value):
        return param_value.strip()

    return stip_spaces

def email_validator(error_msg = None):
    def validate(param_name, param_value):
        if not validate_email.validate_email(str(param_value)):
            if error_msg is not None:
                raise ValueError( error_msg )
            raise ValueError(f"Error: parameter {param_name} is not a valid email")
    return validate

def regex_validator(regular_expression, error_msg = None):
    try:
        regex_compiled = re.compile( regular_expression )
    except re.error as re_error:
        raise ValueError(f"Error: validator {regular_expression} is not a valid regex: " + str(re_error))

    def validate(param_name, param_value):
        if regex_compiled.match(str(param_value)) is None:
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} does not conform to regex {regular_expression}")
        return None

    return validate

def no_regex_validator(regular_expression, error_msg = None):
    try:
        regex_compiled = re.compile( regular_expression )
    except re.error as re_error:
        raise ValueError(f"Error: validator {regular_expression} is not a valid regex: " + str(re_error))

    def validate(param_name, param_value):
        if regex_compiled.match(str(param_value)) is not None:
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} does conform to regex {regular_expression}")

    return validate


def string_list_validator(string_list, error_msg = None):
    string_list_error = ",".join(string_list)

    def validate(param_name, param_value):
        if str(param_value) not in string_list:
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} is not one of {string_list_error}")

    return validate

def max_string_validator(max_length, error_msg = None):

    def validate(param_name, param_value):
        if len(str(param_value)) > max_length:
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} has too many characters")

    return validate

def min_string_validator(min_length, error_msg = None):

    def validate(param_name, param_value):
        if len(str(param_value)) < min_length:
            if error_msg is not None:
                raise ValueError( error_msg )
            raise ValueError( f"Error: parameter {param_name} string is too short" )

    return validate

def string_not_empty_validator(error_msg = None):

    def validate(param_name, param_value):
        if str(param_value) == "":
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} string is empty")

    return validate

def int_list_validator(int_list, error_msg = None):

    string_list_error = ",".join( int_list.map(str))

    def validate(param_name, param_value):
        if int(param_value) not in int_list:
            if error_msg is not None:
                raise ValueError( error_msg )
            raise ValueError( f"Error: parameter {param_name} is not one of {string_list_error}" )

    return validate

class KwArgsChecker:

    def __init__(self, **kwargs):

        if 'required' in kwargs:
            self.map_required_params = kwargs['required']
            KwArgsChecker.__check_def(self.map_required_params)
            #print("required:", self.map_required_params)
        else:
            self.map_required_params = {}

        if 'opt' in kwargs:
            self.map_opt_params = kwargs['opt']
            KwArgsChecker.__check_def(self.map_opt_params)
            #print("opt:", self.map_opt_params)
        else:
            self.map_opt_params = {}

        self.args = {}

    @staticmethod
    def __check_def(param_def):
        type_type=type(str)
        for name, value in param_def.items():
            if isinstance(value, (type([]), type((1,)))):
                for one_value in value:
                    if not isinstance(one_value,(type_type, types.FunctionType)):
                        raise TypeError(f"Error: parameter definition of {name} is not a sequence of types or functions. value: {str(one_value)}")

            elif not isinstance(value,(type_type, types.FunctionType)):
                raise TypeError(f"Error: parameter definition of {name} must be either a type, function, sequence or list of types and functions")


    def validate(self, kwargs_dict):

        for required_param_name in self.map_required_params:
            if not required_param_name in kwargs_dict:
                raise ValueError(f"Error: required parameter {required_param_name} is not passed as parameter")

        for param_name, param_value in kwargs_dict.items():

            entry = self.map_required_params.get( param_name )
            if entry is None:
                entry = self.map_opt_params.get( param_name )
                if entry is None:
                    raise ValueError(f"Error: parameter name {param_name} is not defined")

            if isinstance(entry, type([])) or isinstance(entry, type((1,))):
                for validator in entry:
                    #print("validate list entry validator: ", type(validator), str(validator), "param:", type(param_value), param_value)
                    KwArgsChecker.__validate_one(validator, param_name, param_value, kwargs_dict)
            else:
                #print("validate scalar: ", type(entry), type(param_value), param_value)
                KwArgsChecker.__validate_one(entry, param_name, param_value, kwargs_dict)

    @staticmethod
    def __validate_one( entry, param_name, param_value, args_dict):

        type_type = type(str)

        if isinstance(entry, types.FunctionType):
            new_value = entry( param_name, param_value )
            if new_value is not None:
                args_dict[ param_name ] = new_value
            return True
        if isinstance(entry, type_type):
            if not isinstance(param_value, entry):
                raise ValueError(f"Error: parameter {param_name} not of expected type {str(entry)}")
            return True
        return False

    def copy_kwars(self, **kwargs):
        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value
