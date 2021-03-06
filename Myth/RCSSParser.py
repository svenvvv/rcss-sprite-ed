import tinycss
from tinycss.parsing import ParseError
from functools import reduce

from Myth.Models.Sprite import Sprite


class SpritesheetRule(object):
    at_keyword = '@spritesheet'

    def __init__(self, name, declarations, props, at_rules, line, column, endline):
        self.name = name
        self.props = props
        self.declarations = declarations
        self.at_rules = at_rules
        self.line = line
        self.column = column
        self.endline = endline

    def __repr__(self):
        return ('<{0.__class__.__name__} {0.line}:{0.column}'
                ' {0.name}>'.format(self))


class RCSSProp:
    def __init__(self, type, required):
        self.type = type
        self.required = required

    def cast(self, value):
        if self.type:
            return self.type(value)
        return value


class RCSSParser(tinycss.CSS21Parser):
    def __init__(self):
        # A bit of a HACK :)
        self.hadSpritesheetError = False
        super().__init__()

    def parse_spritesheet_name(self, head):
        if len(head) == 1 and head[0].type == "IDENT":
            return head[0].value
        # NOTE: spritesheet names are optional, so no error logging
        return "UNNAMED"

    def parse_spritesheet_declarations(self, input_decls):
        reservedProps = {
            "src": RCSSProp(str, True),
            "resolution": RCSSProp(float, False)
        }
        reservedPropsGot = []
        props = dict()
        decls = []
        errors = []

        for d in input_decls:
            # A bit of a HACK, in the try block we're checking if it's a reserved prop,
            # which throws on failure and then gets parsed as a regular property ;)
            try:
                rprop = reservedProps[d.name]
                # Since all the reserved props are a single value then concat every token
                # that belongs to these props.
                s = "".join(list(map(lambda v: str(v.value), d.value)))

                reservedPropsGot.append(d.name)

                props[d.name] = rprop.cast(s)
            except KeyError:
                sprite_props = []
                for t in d.value:
                    if t.type == "S":
                        continue
                    sprite_props.append(t.value)

                prop_count = len(sprite_props)
                if prop_count != 4:
                    errors.append(f"Sprite {d.name} has {prop_count} props, expected 4")
                    self.hadSpritesheetError = True
                    continue

                decls.append(Sprite(d.name,
                                    sprite_props[0], sprite_props[1],
                                    sprite_props[2], sprite_props[3]))

        for k,v in reservedProps.items():
            if k not in reservedPropsGot and v.required:
                self.hadSpritesheetError = True
                errors.append(f"Missing required property of type {v.type.__name__}: {k}")

        return decls, props, errors

    def parse_at_rule(self, rule, previous_rules, errors, context):
        if rule.at_keyword == '@spritesheet':
            name = self.parse_spritesheet_name(rule.head)

            if rule.body is None:
                raise ParseError(rule, 'invalid {0} rule: missing block'.format(rule.at_keyword))

            declarations, at_rules, rule_errors = self.parse_declarations_and_at_rules(rule.body, '@spritesheet')
            errors.extend(rule_errors)

            ss_decls, props, decl_errors = self.parse_spritesheet_declarations(declarations)
            errors.extend(decl_errors)

            endline = None

            lasttok = rule.body[-1]
            if lasttok.value == "\n":
                endline = lasttok.line + 1
            else:
                endline = lasttok.line

            return SpritesheetRule(name, ss_decls, props, at_rules, rule.line, rule.column, endline)
        else:
            return super().parse_at_rule(rule, previous_rules, errors, context)

