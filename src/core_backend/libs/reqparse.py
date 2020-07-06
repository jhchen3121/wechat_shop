from copy import deepcopy
import decimal
import six
from exception import Error

class Namespace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


text_type = lambda x: six.text_type(x)


class Argument(object):

    def __init__(self, name, default=None, required=True, type=text_type, 
                    help=None, trim=True, ignore=False, case_sensitive=True):
        self.name = name
        self.default = default
        self.required = required
        self.type = type
        self.help = help
        self.trim = trim
        self.ignore = ignore
        self.case_sensitive = case_sensitive

    def source(self, request):
        return request

    def convert(self, value):
        # Don't cast None
        if value is None:
            return None

        try:
            return self.type(value, self.name, "=")
        except TypeError:
            try:
                if self.type is decimal.Decimal:
                    return self.type(str(value), self.name)
                else:
                    return self.type(value, self.name)
            except TypeError:
                return self.type(value)

    def handle_validation_error(self, error, bundle_errors):
        help_str = '(%s) ' % self.help if self.help else ''
        error_msg = ' '.join([help_str, str(error)]) if help_str else str(error)
        msg = {self.name: "%s" % (error_msg)}
        if bundle_errors:
            return error, msg
        raise Error(400, msg)

    def handle_value(self,value, bundle_errors):
        if hasattr(value, "strip") and self.trim:
            value = value.strip()
        if hasattr(value, "lower") and not self.case_sensitive: 
            value = value.lower()
        
        try:
            value = self.convert(value)
        except Exception as error:
            if self.ignore:
                return True, None 
            return False, self.handle_validation_error(error, bundle_errors)

        return True, value

    def parse(self, request, bundle_errors=False):
        source = self.source(request)

        results = []
        
        # Sentinels
        _not_found = False
        _found = True
        _has_error = False
        
        errors = {}

        if self.name in source:
            values = source[self.name]
                
            if isinstance(values, list): 
                for value in values:
                    f, v = self.handle_value(value, bundle_errors)
                    if f and v: results.append(v)
                    elif not f: return v[0],v[1] 
            else:
                f, v = self.handle_value(values, bundle_errors)
                if f and v: results.append(v)
                elif not f: return v[0],v[1] 

        if not results and self.required:
            error_msg = u"Missing required parameter."
            if bundle_errors:
                return self.handle_validation_error(ValueError(error_msg), bundle_errors)
            self.handle_validation_error(ValueError(error_msg), bundle_errors)

        if not results:
            if callable(self.default):
                return self.default(), _found
            else:
                return self.default, _found
        
        #if len(results) == 1:
        #    return results[0], _found
        return results, _found


class RequestParser(object):
    def __init__(self, argument_class=Argument, namespace_class=Namespace,
            trim=True, bundle_errors=True):
        self.args = []
        self.argument_class = argument_class
        self.namespace_class = namespace_class
        self.trim = trim
        self.bundle_errors = bundle_errors

    def add_argument(self, *args, **kwargs):
        """Adds an argument to be parsed.

        Accepts either a single instance of Argument or arguments to be passed
        into :class:`Argument`'s constructor.

        See :class:`Argument`'s constructor for documentation on the
        available options.
        """

        if len(args) == 1 and isinstance(args[0], self.argument_class):
            self.args.append(args[0])
        else:
            self.args.append(self.argument_class(*args, **kwargs))

        #Do not know what other argument classes are out there
        if self.trim and self.argument_class is Argument:
            #enable trim for appended element
            self.args[-1].trim = kwargs.get('trim', self.trim)

        return self

    def parse_args(self, req=None, strict=False):
        namespace = self.namespace_class()

        errors = {} 
        has_errors = False
        for arg in self.args:
            value, found = arg.parse(req, self.bundle_errors)
            if isinstance(value, ValueError):
                has_errors = True
                errors.update(found)
                found = None
            if found:
                namespace[arg.name] = value
        if has_errors:
            raise Error(400, errors)

        return namespace

    def copy(self):
        """ Creates a copy of this RequestParser with the same set of arguments """
        parser_copy = self.__class__(self.argument_class, self.namespace_class)
        parser_copy.args = deepcopy(self.args)
        parser_copy.trim = self.trim
        parser_copy.bundle_errors = self.bundle_errors
        return parser_copy

    def replace_argument(self, name, *args, **kwargs):
        """ Replace the argument matching the given name with a new version. """
        new_arg = self.argument_class(name, *args, **kwargs)
        for index, arg in enumerate(self.args[:]):
            if new_arg.name == arg.name:
                del self.args[index]
                self.args.append(new_arg)
                break
        return self

    def remove_argument(self, name):
        """ Remove the argument matching the given name. """
        for index, arg in enumerate(self.args[:]):
            if name == arg.name:
                del self.args[index]
                break
        return self

if __name__=="__main__":
    reqparse = RequestParser(bundle_errors=True)
    reqparse.add_argument('name', type=str, required=True, help="user name")
    reqparse.add_argument('address', type=str, required=True, help="user address")
    reqparse.add_argument('age', type=int, required=True, help="user age")
    
    req = dict()
    req["name"] = "guest"
    req["address"]= ["Chengdu","sichuan"]
    req["age"] = 123

    args = reqparse.parse_args(req)
    
    print "args: name:", args["name"]
    print "args: address:", args["address"]
    print "args: age:", args["age"]


