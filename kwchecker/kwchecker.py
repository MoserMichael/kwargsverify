import types
import os
import re
import validate_email

def strip_leading_trailing_space():
    def stip_spaces(_, param_value):
        return str(param_value).strip()

    return stip_spaces

def _sanitize_db_imp(_param_name, param_value):
    if isinstance(param_value, str):
        return str(param_value).replace("'","").replace('"',"")
    return None

def sanitize_db():
    return _sanitize_db_imp

def to_lower_case():
    def to_lower(_param_name, param_value):
        return str(param_value).lower()

    return to_lower

def to_upper_case():
    def to_upper(_param_name, param_value):
        return str(param_value).upper()

    return to_upper

def capitalize_first_letter():
    def to_upper(_param_name, param_value):
        return str(param_value).title()

    return to_upper



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

def sanitize_file_path():
    def validate(_param_name, param_value):
        return os.path.normpath(param_value)
    return validate

def file_exists_validator(error_msg = None):
    def validate(_param_name, param_value):
        if not os.path.exists(param_value):
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: file {param_value} does not exist")

    return validate

def file_readable_validator(error_msg = None):
    def validate(_param_name, param_value):
        if not os.path.exists(str(param_value)):
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: file {param_value} does not exist")
        if not os.access(str(param_value), os.R_OK):
            raise ValueError(f"Error: file {param_value} is not readable")

    return validate

def file_writable_validator(error_msg = None):
    def validate(_param_name, param_value):
        if not os.path.exists(str(param_value)):
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: file {param_value} does not exist")
        if not os.access(str(param_value), os.W_OK):
            raise ValueError(f"Error: file {param_value} is not writable")

    return validate

def file_executable_validator(error_msg = None):

    def validate(_param_name, param_value):
        if not os.path.exists(str(param_value)):
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: file {param_value} does not exist")
        if not os.access(str(param_value), os.X_OK):
            raise ValueError(f"Error: file {param_value} is not executable")

    return validate


def string_list_validator(string_list, error_msg = None):
    string_list_error = ",".join(string_list)

    def validate(param_name, param_value):
        if str(param_value) not in string_list:
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} is not one of {string_list_error}")

    return validate


def string_validator(string_list, separator = None, error_msg = None):
    string_list_error = ",".join(string_list)

    def validate(param_name, param_value):
        for val in map(str.strip, param_value.split(separator)):
            if str(val) not in string_list:
                if error_msg is not None:
                    raise ValueError(error_msg)
                raise ValueError(f"Error: parameter {param_name}, the value {val} is not one of {string_list_error}")

    return validate


def max_string_validator(max_length, error_msg = None):

    def validate(param_name, param_value):
        if len(str(param_value)) > max_length:
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} has more than {max_length} characters")

    return validate

def min_string_validator(min_length, error_msg = None):

    def validate(param_name, param_value):
        if len(str(param_value)) < min_length:
            if error_msg is not None:
                raise ValueError( error_msg )
            raise ValueError( f"Error: parameter {param_name} string has fewer than {min_length} characters")

    return validate

def string_not_empty_validator(error_msg = None):

    def validate(param_name, param_value):
        if str(param_value) == "":
            if error_msg is not None:
                raise ValueError(error_msg)
            raise ValueError(f"Error: parameter {param_name} string may not be empty")

    return validate

def int_range_validator(from_int, to_int, error_msg = None):

    def validate(param_name, param_value):
        if int(param_value) < from_int or int(param_value) > to_int:
            if error_msg is not None:
                raise ValueError( error_msg )
            raise ValueError( f"Error: parameter {param_name} must be between {from_int} to {to_int}" )

    return validate

def int_list_validator(int_list, error_msg = None):

    string_list_error = ",".join( int_list.map(str))

    def validate(param_name, param_value):
        if int(param_value) not in int_list:
            if error_msg is not None:
                raise ValueError( error_msg )
            raise ValueError( f"Error: parameter {param_name} is not one of {string_list_error}" )

    return validate

def int_list_mask(masks, error_msg = None):

    string_list_error = ",".join( masks.map(hex) )

    def validate(param_name, param_value):

        for mask in masks:
            if int(param_value) & ~mask != 0:
                if error_msg is not None:
                    raise ValueError( error_msg )
                raise ValueError( f"Error: parameter {param_name} is not in the bit masks {string_list_error}" )

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
        
        if 'on_all_pre' in kwargs:
            self.act_on_all_pre = kwargs['on_all_pre']
        else:
            self.act_on_all_pre = None

        if 'on_all_post' in kwargs:
            self.act_on_all_post = kwargs['on_all_post']
        else:
            self.act_on_all_post = None


#        if 'sanitize_db' in kwargs:
#            self.sanitize_db = True
#        else:
#            self.sanitize_db = True

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

            if self.act_on_all_pre is not None:
                KwArgsChecker.__validate( self.act_on_all_pre, param_name, param_value, kwargs_dict)

            KwArgsChecker.__validate( entry, param_name, param_value, kwargs_dict)

            if self.act_on_all_post is not None:
                KwArgsChecker.__validate( self.act_on_all_post, param_name, param_value, kwargs_dict)

#            if self.sanitize_db:
#                val = _sanitize_db_imp(None, param_value)
#                if val is not None:
#                    kwargs_dict[ param_name ] = val

    @staticmethod
    def __validate( entry, param_name, param_value, args_dict):
        if isinstance(entry, (type([]), type((1,)))):
            for validator in entry:
                #print("validate list entry validator: ", type(validator), str(validator), "param:", type(param_value), param_value)
                val = KwArgsChecker.__validate_one(validator, param_name, param_value, args_dict)
                if val is not None:
                    param_value = val
        else:
            #print("validate scalar: ", type(entry), type(param_value), param_value)
            KwArgsChecker.__validate_one(entry, param_name, param_value, args_dict)



    @staticmethod
    def __validate_one( entry, param_name, param_value, args_dict):

        type_type = type(str)

        if isinstance(entry, types.FunctionType):
            new_value = entry( param_name, param_value )
            if new_value is not None:
                args_dict[ param_name ] = new_value
                return new_value
        elif isinstance(entry, type_type):
            if not isinstance(param_value, entry):
                raise ValueError(f"Error: parameter {param_name} not of expected type {str(entry)}")
        return None

    def copy_kwars(self, **kwargs):
        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value
