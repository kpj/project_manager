import sys

from jsonschema import validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS['properties']

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if 'default' in subschema:
                instance.setdefault(property, subschema['default'])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {'properties': set_defaults})


def validate_config(data, schema):
    Validator = validators.validator_for(schema)
    DefaultValidator = extend_with_default(Validator)

    v = DefaultValidator(schema)
    if not v.is_valid(data):
        print('Invalid config:')
        for error in v.iter_errors(data):
            print(f' - {error.message}')
        print('Aborting...')
        sys.exit(-1)

    return data


def main(data):
    schema = {
        'definitions': {
            'config_items': {
                'type': 'object',
                'properties': {
                    'key': {'type': ['string', 'array']},
                    'values': {'type': 'array'},
                    'paired': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/config_items'}
                    }
                },
                'additionalProperties': False,
                'required': ['key', 'values']
            }
        },

        'type': 'object',
        'properties': {
            'project_source': {'type': 'string'},
            'working_dir': {'type': 'string'},

            'exec_command': {
                'type': 'array',
                'items': {'type': 'string'},
                'default': []
            },
            'result_dirs': {
                'type': 'array',
                'items': {'type': 'string'},
                'default': []
            },
            'symlinks': {
                'type': 'array',
                'items': {'type': 'string'},
                'default': []
            },

            'base_config': {'type': 'string'},
            'config_parameters': {
                'type': 'array',
                'items': {'$ref': '#/definitions/config_items'}
            },
            'extra_parameters': {
                'type': 'object',
                'properties': {
                    'git_branch': {
                        'type': 'array'
                    },
                    'repetitions': {
                        'type': 'integer',
                        'default': 1
                    }
                },
                'additionalProperties': False,
                'default': {'repetitions': 1}
            }
        },
        'additionalProperties': False,
        'required': ['project_source', 'working_dir', 'base_config']
    }

    return validate_config(data, schema)


if __name__ == '__main__':
    print(main({
        'project_source': 'foo',
        'working_dir': 'bar',
        'base_config': 'baz'
    }))
