import abc

import attr
import validator


def attrib(validation=None):
    return attr.ib(metadata={'validation': validation})


class ValidationError(ValueError):
    pass


class DTOMeta(abc.ABCMeta):
    def __new__(mcs, name, bases, dict):
        new_class = super().__new__(mcs, name, bases, dict)
        return attr.s(new_class)


class BaseDTO(metaclass=DTOMeta):

    @property
    def validation_rules(self) -> dict:
        result = {}

        for field in attr.fields(self.__class__):
            validation_rules = field.metadata.get('validation')
            if validation_rules:
                result[field.name] = [validator.InstanceOf(field.type)] + validation_rules

        return result

    def validate(self) -> dict:
        pass

    def __attrs_post_init__(self):
        valid, errors = validator.validate(self.validation_rules, attr.asdict(self))
        if not valid:
            raise ValidationError(errors)
