from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=254))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    invitationKey = fields.Str(required=True, validate=validate.Length(min=1, max=32))


class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=254))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=20))
