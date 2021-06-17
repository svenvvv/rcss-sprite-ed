import tinycss
from functools import reduce

from Myth.Sprite import Sprite

class SpritesheetRule(object):
    at_keyword = '@spritesheet'

    def __init__(self, name, declarations, props, at_rules, line, column):
        self.name = name
        self.props = props
        self.declarations = declarations
        self.at_rules = at_rules
        self.line = line
        self.column = column

    def __repr__(self):
        return ('<{0.__class__.__name__} {0.line}:{0.column}'
                ' {0.name}>'.format(self))

class RCSSParser(tinycss.CSS21Parser):
    def parse_spritesheet_name(self, head):
        if len(head) == 1 and head[0].type == "IDENT":
            return head[0].value
        # NOTE: spritesheet names are optional, so no error logging
        return "UNNAMED"

    def parse_spritesheet_declarations(self, input_decls):
        spritesheet_reserved_props = [ "src", "resolution" ]
        props = dict()
        decls = []
        errors = []

        for d in input_decls:
            if d.name in spritesheet_reserved_props:
                # NOTE: Since all the reserved props are a single value then concat every token
                # that belongs to these props.
                s = "".join(list(map(lambda v: str(v.value), d.value)))
                props[d.name] = s
            else:
                sprite_props = []
                for t in d.value:
                    if t.type == "S":
                        continue
                    sprite_props.append(t.value)

                prop_count = len(sprite_props)
                if prop_count != 4:
                    errors.append(f"Sprite {d.name} has {prop_count} props, expected 4")
                    continue

                decls.append(Sprite(d.name,
                                    sprite_props[0], sprite_props[1],
                                    sprite_props[2], sprite_props[3]))

        return decls, props, errors

    def parse_at_rule(self, rule, previous_rules, errors, context):
        if rule.at_keyword == '@spritesheet':
            if context != 'stylesheet':
                raise ParseError(rule, '@spritesheet rule not allowed in ' + context)
            name = self.parse_spritesheet_name(rule.head)
            if rule.body is None:
                raise ParseError(rule, 'invalid {0} rule: missing block'.format(rule.at_keyword))
            declarations, at_rules, rule_errors = self.parse_declarations_and_at_rules(rule.body, '@spritesheet')
            errors.extend(rule_errors)
            ss_decls, props, decl_errors = self.parse_spritesheet_declarations(declarations)
            errors.extend(decl_errors)
            return SpritesheetRule(name, ss_decls, props, at_rules, rule.line, rule.column)
        else:
            return super().parse_at_rule(rule, previous_rules, errors, context)

